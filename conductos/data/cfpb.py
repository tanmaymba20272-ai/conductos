"""CFPB consumer complaints: archive sampling (primary) and live API (metadata only).

On 14 Aug 2026 the CFPB stopped publishing complaint narratives in its live database. Narratives
published before then are in the FOIA narratives archive (zip exports). ConductOS therefore builds
a fixed, seeded golden sample from the archive once, and evaluates every model version against it.
The live API is kept for metadata-only uses (it no longer returns `complaint_what_happened`).

No API key is needed. CFPB already scrubs personal data in narratives as XXXX.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

from conductos.data.taxonomy import map_product

API = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"


@dataclass(frozen=True)
class Complaint:
    complaint_id: str
    date_received: str
    narrative: str
    cfpb_product: str
    cfpb_sub_product: str | None
    cfpb_issue: str | None
    company: str | None
    state: str | None
    company_response: str | None
    product_label: str  # operational key (consumer-chosen label, mapped)


def _rows(payload: object) -> list[dict]:
    """The API returns either Elasticsearch-style hits or a flat list depending on params."""
    if isinstance(payload, list):
        return [r.get("_source", r) for r in payload]
    if isinstance(payload, dict) and "hits" in payload:
        return [h.get("_source", h) for h in payload["hits"]["hits"]]
    raise ValueError("Unrecognized CFPB API response shape")


def parse(rows: list[dict]) -> list[Complaint]:
    out: list[Complaint] = []
    for r in rows:
        narrative = (r.get("complaint_what_happened") or "").strip()
        label = map_product(r.get("product"), r.get("sub_product"))
        if not narrative or not label:
            continue
        out.append(
            Complaint(
                complaint_id=str(r.get("complaint_id")),
                date_received=str(r.get("date_received", ""))[:10],
                narrative=narrative,
                cfpb_product=r.get("product", ""),
                cfpb_sub_product=r.get("sub_product"),
                cfpb_issue=r.get("issue"),
                company=r.get("company"),
                state=r.get("state"),
                company_response=r.get("company_response"),
                product_label=label,
            )
        )
    return out


PAGE = 100


def _get(params: dict, timeout: int, attempts: int = 3) -> object:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (conductos research; +https://github.com/tanmaymba20272-ai/conductos)",
        "Accept": "application/json",
    })
    last: Exception | None = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body = e.read(300).decode("utf-8", "replace")
            last = RuntimeError(f"CFPB API HTTP {e.code} for {url}: {body}")
        except Exception as e:  # noqa: BLE001
            last = RuntimeError(f"CFPB API {type(e).__name__} for {url}: {e}")
        time.sleep(2 * (i + 1))
    raise last  # type: ignore[misc]


def fetch(n: int = 500, date_min: str = "2025-01-01", timeout: int = 60) -> list[Complaint]:
    """Fetch up to n recent complaints with narratives, paging 100 at a time."""
    out: list[Complaint] = []
    seen: set[str] = set()
    frm = 0
    while len(out) < n and frm < n * 4:  # over-fetch: some rows won't map
        payload = _get({
            "size": PAGE,
            "frm": frm,
            "has_narrative": "true",
            "date_received_min": date_min,
            "sort": "created_date_desc",
            "no_aggs": "true",
        }, timeout)
        rows = _rows(payload)
        if not rows:
            break
        for c in parse(rows):
            if c.complaint_id not in seen:
                seen.add(c.complaint_id)
                out.append(c)
        frm += PAGE
    if not out:
        raise RuntimeError("CFPB API returned no usable complaints (check filters or API changes)")
    return out[:n]


def save_jsonl(complaints: list[Complaint], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for c in complaints:
            f.write(json.dumps(asdict(c)) + "\n")


def load_jsonl(path: Path) -> list[Complaint]:
    with path.open() as f:
        return [Complaint(**json.loads(line)) for line in f if line.strip()]


# ---------------------------------------------------------------- archive sampling

ARCHIVE_PAGE = "https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/"
DEFAULT_ARCHIVE = "https://files.consumerfinance.gov/f/documents/CCDB_Export_20_July_2026.zip"

# Export column names vary (CSV headers vs API-style keys). Normalise to the API field names.
_ALIASES = {
    "consumer_complaint_narrative": "complaint_what_happened",
    "complaint_what_happened": "complaint_what_happened",
    "narrative": "complaint_what_happened",
    "complaint_id": "complaint_id",
    "date_received": "date_received",
    "product": "product",
    "sub_product": "sub_product",
    "issue": "issue",
    "sub_issue": "sub_issue",
    "company": "company",
    "state": "state",
    "company_response_to_consumer": "company_response",
    "company_response": "company_response",
}


def _norm_key(k: str) -> str:
    k = k.strip().lower().replace("?", "")
    for ch in " -/":
        k = k.replace(ch, "_")
    return _ALIASES.get(k, k)


def _norm_row(row: dict) -> dict:
    return {_norm_key(k): v for k, v in row.items() if k is not None}


def _iter_archive_rows(zip_path: Path):
    """Yield normalised rows from every CSV / JSON / JSONL member of an export zip."""
    import csv
    import io
    import sys
    import zipfile

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.namelist() if m.lower().endswith((".csv", ".json", ".jsonl"))]
        if not members:
            raise RuntimeError(f"No CSV/JSON files in {zip_path.name}: {zf.namelist()[:10]}")
        for name in members:
            with zf.open(name) as raw:
                if name.lower().endswith(".csv"):
                    for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")):
                        yield _norm_row(row)
                elif name.lower().endswith(".jsonl"):
                    for line in io.TextIOWrapper(raw, encoding="utf-8", errors="replace"):
                        if line.strip():
                            yield _norm_row(json.loads(line))
                else:
                    data = json.load(raw)
                    for row in _rows(data) if not isinstance(data, list) else data:
                        yield _norm_row(row.get("_source", row))


def sample_archive(zip_path: Path, n: int = 1000, seed: int = 2026) -> tuple[list[Complaint], dict]:
    """Seeded reservoir sample of n usable complaints (narrative + mappable product)."""
    import random

    rng = random.Random(seed)
    reservoir: list[dict] = []
    stats = {"rows": 0, "usable": 0}
    for row in _iter_archive_rows(zip_path):
        stats["rows"] += 1
        if not parse([row]):
            continue
        stats["usable"] += 1
        if len(reservoir) < n:
            reservoir.append(row)
        else:
            j = rng.randrange(stats["usable"])
            if j < n:
                reservoir[j] = row
    if stats["rows"] and not stats["usable"]:
        first = next(_iter_archive_rows(zip_path))
        raise RuntimeError(f"Archive rows found but none usable; columns seen: {sorted(first)[:25]}")
    out = sorted(parse(reservoir), key=lambda c: c.complaint_id)
    return out, stats


def download(url: str, dest: Path, timeout: int = 600) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (conductos research)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as f:
        while chunk := resp.read(1 << 20):
            f.write(chunk)
    return dest
