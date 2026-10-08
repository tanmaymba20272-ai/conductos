"""Fetch complaints from the public CFPB Consumer Complaint Database API.

No API key is needed. We only take complaints that include a consumer narrative
(published with the consumer's consent; CFPB already scrubs personal data as XXXX).
"""

from __future__ import annotations

import json
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


def fetch(n: int = 500, date_min: str = "2025-01-01", timeout: int = 60) -> list[Complaint]:
    """Fetch up to n recent complaints with narratives."""
    params = {
        "size": min(n * 2, 10000),  # over-fetch: some rows won't map
        "has_narrative": "true",
        "date_received_min": date_min,
        "sort": "created_date_desc",
        "no_aggs": "true",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "conductos-research/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.load(resp)
    return parse(_rows(payload))[:n]


def save_jsonl(complaints: list[Complaint], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for c in complaints:
            f.write(json.dumps(asdict(c)) + "\n")


def load_jsonl(path: Path) -> list[Complaint]:
    with path.open() as f:
        return [Complaint(**json.loads(line)) for line in f if line.strip()]
