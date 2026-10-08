"""Case state machine (PRD-B §7.2). Illegal transitions are rejected in code, not by prompts."""

from __future__ import annotations

from enum import Enum


class State(str, Enum):
    RECEIVED = "received"
    QUARANTINED = "quarantined"
    TRIAGED = "triaged"
    AUTO_RESOLVED = "auto_resolved"
    INVESTIGATING = "investigating"
    DRAFTED = "drafted"
    COMPLIANCE_CHECK = "compliance_check"
    HUMAN_REVIEW = "human_review"
    RESOLVED = "resolved"


ALLOWED: dict[State, set[State]] = {
    State.RECEIVED: {State.QUARANTINED, State.TRIAGED},
    State.QUARANTINED: {State.HUMAN_REVIEW},
    State.TRIAGED: {State.AUTO_RESOLVED, State.INVESTIGATING, State.HUMAN_REVIEW},
    State.INVESTIGATING: {State.DRAFTED, State.HUMAN_REVIEW},
    State.DRAFTED: {State.COMPLIANCE_CHECK},
    State.COMPLIANCE_CHECK: {State.HUMAN_REVIEW, State.RESOLVED},
    State.HUMAN_REVIEW: {State.RESOLVED, State.INVESTIGATING},
    State.AUTO_RESOLVED: set(),
    State.RESOLVED: set(),
}


class IllegalTransition(Exception):
    pass


class Case:
    def __init__(self, case_id: str) -> None:
        self.case_id = case_id
        self.state = State.RECEIVED
        self.history: list[tuple[State, State, str]] = []

    def transition(self, to: State, reason: str) -> None:
        if to not in ALLOWED[self.state]:
            raise IllegalTransition(f"{self.case_id}: {self.state.value} -> {to.value} not allowed")
        self.history.append((self.state, to, reason))
        self.state = to
