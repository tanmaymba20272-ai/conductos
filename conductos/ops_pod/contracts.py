"""Typed contracts between agents (PRD-B §7.2). Agents exchange these, never free text."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class _Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    schema_version: str = "1.0"


class CleanCase(_Contract):
    case_id: str
    text: str = Field(min_length=1)
    received: str
    source: str = "cfpb"


class TriageDecision(_Contract):
    case_id: str
    trace_id: str
    model: str
    backend: str
    sub_team: str | None
    sub_team_probabilities: dict[str, float]
    severity: int | None = Field(default=None, ge=0, le=3)
    severity_probabilities: dict[str, float] = {}
    vulnerable_p: float | None = None
    regulatory_risk_p: float | None = None  # max of risk_flags
    risk_flags: dict[str, float] = {}
    injection_p: float | None = None
    latency_ms: float
    cost_usd: float


class Route(str, Enum):
    AUTO = "auto"            # act at the action's current autonomy level
    REVIEW = "human_review"  # human decides
    INVESTIGATE = "investigate"  # escalate to System Two, then human
    QUARANTINE = "quarantine"    # suspected injection: no LLM may see it


class RoutingDecision(_Contract):
    case_id: str
    route: Route
    reasons: list[str]
    calibrated_routing_p: float | None
    autonomy_level: str
    suggested_sub_team: str | None = None  # assist mode: the team a reviewer confirms or corrects
