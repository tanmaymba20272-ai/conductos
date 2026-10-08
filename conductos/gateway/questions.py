"""Vendor-neutral decision contract.

Workflows describe *what* they want decided with these types. Backends translate them
(Jev via the TypeSafe SDK, rules, or an LLM adapter). Keeping the contract ours is the
hedge against vendor lock-in recorded in ADR-001.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChoiceQ:
    instructions: str
    criteria: dict[str, str]

    def __post_init__(self) -> None:
        if not 2 <= len(self.criteria) <= 255:
            raise ValueError("Choice needs 2-255 options (Jev limit)")


@dataclass(frozen=True)
class ScoreQ:
    instructions: str
    levels: list[str]  # ordered, lowest first


@dataclass(frozen=True)
class NoulQ:
    instructions: str


Question = ChoiceQ | ScoreQ | NoulQ


@dataclass
class Answer:
    kind: str  # "choice" | "score" | "noul"
    value: str | int | float | None
    probabilities: dict[str, float] = field(default_factory=dict)
    confidence: float | None = None  # vendor "confidence" = peakedness, NOT calibrated

    @property
    def top_probability(self) -> float | None:
        if self.kind == "noul" and isinstance(self.value, float):
            return max(self.value, 1 - self.value)
        return max(self.probabilities.values()) if self.probabilities else None
