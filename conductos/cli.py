"""ConductOS command line.

    conductos build-sample --n 1000           # one-off: seeded golden sample from the CFPB archive
    conductos triage   --backend jev           # System One triage + supervisor routing
    conductos evaluate                         # harness report -> results/latest.{json,md}
    conductos skeleton --n 500                 # all of the above (walking skeleton)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

from conductos.data import cfpb
from conductos.eval_harness.report import evaluate, to_markdown
from conductos.gateway import Gateway
from conductos.gateway.backends import JevBackend, RulesBackend
from conductos.ops_pod.contracts import CleanCase
from conductos.ops_pod.state_machine import Case, State
from conductos.ops_pod.supervisor import load_policy, route
from conductos.ops_pod.triage import RULES_KEYWORDS, triage

GOLDEN = Path("data/golden/cfpb_sample.jsonl")  # fixed, seeded sample from the CFPB narratives archive
RUNS = Path("results/runs")
LATEST = Path("results")


def _load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def cmd_build_sample(a: argparse.Namespace) -> None:
    zip_path = Path(a.zip) if a.zip else cfpb.download(a.url, Path("data/raw") / Path(a.url).name)
    print(f"Sampling {a.n} complaints from {zip_path} (seed {a.seed})")
    complaints, stats = cfpb.sample_archive(zip_path, n=a.n, seed=a.seed)
    cfpb.save_jsonl(complaints, GOLDEN)
    meta = {"source": a.url if not a.zip else str(a.zip), "seed": a.seed, **stats, "sampled": len(complaints),
            "label_mix": dict(Counter(c.product_label for c in complaints))}
    GOLDEN.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


def _source() -> Path:
    if GOLDEN.exists():
        return GOLDEN
    raise RuntimeError("No complaint sample found. Run `conductos build-sample` first (or the build-sample workflow).")


def _run(backend_name: str, complaints: list[cfpb.Complaint]) -> list[dict]:
    if backend_name == "jev":
        chain = [JevBackend(), RulesBackend(RULES_KEYWORDS)]  # rules = fallback
    else:
        chain = [RulesBackend(RULES_KEYWORDS)]
    gw = Gateway(chain=chain, trace_path=RUNS / f"traces-{backend_name}.jsonl")
    policy = load_policy()
    calibrator = _load_calibrator()
    out = []
    routes: Counter[str] = Counter()
    for i, c in enumerate(complaints, 1):
        case = Case(c.complaint_id)
        clean = CleanCase(case_id=c.complaint_id, text=c.narrative, received=c.date_received)
        t = triage(clean, gw)
        rd = route(t, policy, calibrator)
        routes[rd.route.value] += 1
        if rd.route.value == "quarantine":
            case.transition(State.QUARANTINED, "; ".join(rd.reasons))
        else:
            case.transition(State.TRIAGED, "triage complete")
        out.append({**t.model_dump(), "label": c.product_label, "route": rd.route.value, "route_reasons": rd.reasons})
        if i % 50 == 0:
            print(f"  {backend_name}: {i}/{len(complaints)}", file=sys.stderr)
    print(f"{backend_name} routes: {dict(routes)}")
    return out


def _load_calibrator():
    path = LATEST / "latest.json"
    if not path.exists():
        return None
    cal = json.loads(path.read_text()).get("calibrator")
    if not cal:
        return None
    from conductos.eval_harness.metrics import IsotonicCalibrator
    import numpy as np

    c = IsotonicCalibrator()
    c.x_, c.y_ = np.array(cal["x"]), np.array(cal["y"])
    return c


def _write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def cmd_triage(a: argparse.Namespace) -> None:
    complaints = cfpb.load_jsonl(_source())[: a.n]
    rows = _run(a.backend, complaints)
    _write_jsonl(rows, RUNS / f"decisions-{a.backend}.jsonl")


def cmd_evaluate(a: argparse.Namespace) -> None:
    primary = _read_jsonl(RUNS / "decisions-jev.jsonl")
    base_path = RUNS / "decisions-rules.jsonl"
    baseline = _read_jsonl(base_path) if base_path.exists() else None
    report = evaluate(primary, baseline, target=a.target)
    LATEST.mkdir(parents=True, exist_ok=True)
    (LATEST / "latest.json").write_text(json.dumps(report, indent=2))
    (LATEST / "latest.md").write_text(to_markdown(report))
    print(to_markdown(report))
    if a.publish:
        dest = Path(a.publish)
        dest.parent.mkdir(parents=True, exist_ok=True)
        public = {k: v for k, v in report.items() if k != "calibrator"}
        dest.write_text(json.dumps(public, indent=2))
        print(f"Published summary -> {dest}")


def cmd_skeleton(a: argparse.Namespace) -> None:
    a.backend = "rules"
    cmd_triage(a)
    a.backend = "jev"
    cmd_triage(a)
    cmd_evaluate(a)


def main(argv: list[str] | None = None) -> None:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="conductos")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build-sample")
    b.add_argument("--n", type=int, default=1000)
    b.add_argument("--seed", type=int, default=2026)
    b.add_argument("--url", default=cfpb.DEFAULT_ARCHIVE)
    b.add_argument("--zip", help="use an already-downloaded export zip instead of --url")
    b.set_defaults(func=cmd_build_sample)

    t = sub.add_parser("triage")
    t.add_argument("--backend", choices=["jev", "rules"], default="jev")
    t.add_argument("--n", type=int, default=500)
    t.set_defaults(func=cmd_triage)

    e = sub.add_parser("evaluate")
    e.add_argument("--target", type=float, default=0.95)
    e.add_argument("--publish", help="also write a public summary JSON here (e.g. for the portfolio site)")
    e.set_defaults(func=cmd_evaluate)

    s = sub.add_parser("skeleton")
    s.add_argument("--n", type=int, default=500)
    s.add_argument("--target", type=float, default=0.95)
    s.add_argument("--publish")
    s.set_defaults(func=cmd_skeleton)

    args = p.parse_args(argv)
    needs_jev = args.cmd == "skeleton" or (args.cmd == "triage" and args.backend == "jev")
    if needs_jev and not os.environ.get("TYPESAFE_API_KEY"):
        _fail("TYPESAFE_API_KEY is not set. Locally: copy .env.example to .env. In GitHub: add it as a repository secret.")
    try:
        args.func(args)
    except Exception as e:  # noqa: BLE001
        _fail(f"{args.cmd} failed: {type(e).__name__}: {e}")


def _fail(msg: str) -> None:
    # In GitHub Actions, surface the reason as an annotation so it is visible without the raw log.
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error title=conductos::{msg.replace(chr(10), ' ')[:900]}")
    sys.exit(msg)


if __name__ == "__main__":
    main()
