"""ConductOS command line.

    conductos fetch    --n 500                 # CFPB complaints -> data/raw/cfpb.jsonl
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

RAW = Path("data/raw/cfpb.jsonl")
RUNS = Path("results/runs")
LATEST = Path("results")


def _load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def cmd_fetch(a: argparse.Namespace) -> None:
    complaints = cfpb.fetch(n=a.n, date_min=a.since)
    cfpb.save_jsonl(complaints, RAW)
    print(f"Saved {len(complaints)} complaints -> {RAW}")
    print("Label mix:", dict(Counter(c.product_label for c in complaints)))


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
    complaints = cfpb.load_jsonl(RAW)[: a.n]
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
    if not RAW.exists() or a.refetch:
        cmd_fetch(a)
    a.backend = "rules"
    cmd_triage(a)
    a.backend = "jev"
    cmd_triage(a)
    cmd_evaluate(a)


def main(argv: list[str] | None = None) -> None:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="conductos")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch")
    f.add_argument("--n", type=int, default=500)
    f.add_argument("--since", default="2025-01-01")
    f.set_defaults(func=cmd_fetch)

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
    s.add_argument("--since", default="2025-01-01")
    s.add_argument("--target", type=float, default=0.95)
    s.add_argument("--refetch", action="store_true")
    s.add_argument("--publish")
    s.set_defaults(func=cmd_skeleton)

    args = p.parse_args(argv)
    needs_jev = args.cmd == "skeleton" or (args.cmd == "triage" and args.backend == "jev")
    if needs_jev and not os.environ.get("TYPESAFE_API_KEY"):
        sys.exit("TYPESAFE_API_KEY is not set. Copy .env.example to .env and add your key.")
    args.func(args)


if __name__ == "__main__":
    main()
