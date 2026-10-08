"""Agentic Gateway (Pillar A) — thin v1.

Every decision call goes through `Gateway.decide`, which:
  1. redacts PII from the state (input guardrail),
  2. calls the primary backend, falling back down the chain on error,
  3. records a trace event (latency, model, tokens, cost, fallback, redactions).

Traces are plain dicts written to JSONL; an OpenTelemetry exporter is on the roadmap (PRD-A v2).
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from conductos.gateway.backends import BackendResult, DecisionBackend
from conductos.gateway.questions import Question
from conductos.gateway.redaction import redact


@dataclass
class Decision:
    trace_id: str
    result: BackendResult
    backend: str
    fallback_used: bool
    latency_ms: float
    redactions: int


@dataclass
class Gateway:
    chain: list[DecisionBackend]
    trace_path: Path | None = None
    killed: bool = False
    _traces: list[dict] = field(default_factory=list)

    def kill(self) -> None:
        """Kill switch: all subsequent decisions raise, so workflows route to humans."""
        self.killed = True

    def decide(self, state: str, questions: dict[str, Question], workflow: str = "m1") -> Decision:
        if self.killed:
            raise RuntimeError("Gateway kill switch is on; route to human review")
        clean, n_redacted = redact(state)
        errors: list[str] = []
        for i, backend in enumerate(self.chain):
            t0 = time.perf_counter()
            try:
                result = backend.decide(clean, questions)
            except Exception as e:  # noqa: BLE001 - any backend failure triggers fallback
                errors.append(f"{backend.name}: {type(e).__name__}")
                continue
            latency = (time.perf_counter() - t0) * 1000
            decision = Decision(
                trace_id=uuid.uuid4().hex,
                result=result,
                backend=backend.name,
                fallback_used=i > 0,
                latency_ms=latency,
                redactions=n_redacted,
            )
            self._trace(decision, workflow, errors)
            return decision
        raise RuntimeError(f"All backends failed: {errors}")

    def _trace(self, d: Decision, workflow: str, errors: list[str]) -> None:
        event = {
            "trace_id": d.trace_id,
            "ts": time.time(),
            "workflow": workflow,
            "backend": d.backend,
            "model": d.result.model,
            "fallback_used": d.fallback_used,
            "errors": errors,
            "latency_ms": round(d.latency_ms, 1),
            "input_tokens": d.result.input_tokens,
            "cost_usd": d.result.cost_usd,
            "redactions": d.redactions,
        }
        self._traces.append(event)
        if self.trace_path:
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)
            with self.trace_path.open("a") as f:
                f.write(json.dumps(event) + "\n")

    @property
    def traces(self) -> list[dict]:
        return list(self._traces)
