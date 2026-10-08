"""Supervisor agent: a deterministic policy engine (ADR-004, ADR-005).

It never asks a model what to do. It reads the autonomy policy, the calibrator published by
the eval harness, and the triage decision, then routes the case.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import yaml

from conductos.data.taxonomy import group_probabilities
from conductos.ops_pod.contracts import Route, RoutingDecision, TriageDecision

DEFAULT_POLICY = Path(__file__).resolve().parents[2] / "policy" / "autonomy.yaml"


def load_policy(path: Path = DEFAULT_POLICY) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def route(
    t: TriageDecision,
    policy: dict,
    calibrate: Callable[[float], float] | None = None,
) -> RoutingDecision:
    mr = policy["mandatory_review"]
    reasons: list[str] = []
    level = policy["actions"]["route_to_queue"]["current"]

    if (t.injection_p or 0) >= mr["injection_p_quarantine"]:
        return RoutingDecision(case_id=t.case_id, route=Route.QUARANTINE,
                               reasons=["suspected prompt injection"], calibrated_routing_p=None,
                               autonomy_level=level)

    # ADR-007: autonomy keys on the routing group, not the product tag.
    raw = max(group_probabilities(t.product_probabilities).values()) if t.product_probabilities else None
    cal = calibrate(raw) if (calibrate and raw is not None) else None

    if (t.vulnerable_p or 0) >= mr["vulnerable_customer_p"]:
        reasons.append("vulnerable-customer signal")
    if (t.regulatory_risk_p or 0) >= mr["regulatory_risk_p"]:
        reasons.append("regulatory-risk flag")
    if t.severity is not None and t.severity >= mr["severity_at_least"]:
        reasons.append("critical severity")
    if reasons:
        return RoutingDecision(case_id=t.case_id, route=Route.REVIEW, reasons=reasons,
                               calibrated_routing_p=cal, autonomy_level=level)

    th = policy["thresholds"]["routing_group"]
    if cal is None or th["auto"] is None:
        return RoutingDecision(case_id=t.case_id, route=Route.REVIEW,
                               reasons=["no calibrated threshold published yet"],
                               calibrated_routing_p=cal, autonomy_level=level)
    if cal >= th["auto"]:
        return RoutingDecision(case_id=t.case_id, route=Route.AUTO,
                               reasons=[f"calibrated p {cal:.2f} >= auto {th['auto']}"],
                               calibrated_routing_p=cal, autonomy_level=level)
    if cal >= th["review"]:
        return RoutingDecision(case_id=t.case_id, route=Route.REVIEW,
                               reasons=[f"calibrated p {cal:.2f} in review band"],
                               calibrated_routing_p=cal, autonomy_level=level)
    return RoutingDecision(case_id=t.case_id, route=Route.INVESTIGATE,
                           reasons=[f"calibrated p {cal:.2f} below review band: abstain"],
                           calibrated_routing_p=cal, autonomy_level=level)
