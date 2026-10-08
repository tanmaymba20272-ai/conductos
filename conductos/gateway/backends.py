"""Decision backends behind the gateway.

- JevBackend: TypeSafe Jev (System One) via the official SDK.
- RulesBackend: keyword baseline. Used as a fallback and as the benchmark the AI must beat.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from conductos.gateway.questions import Answer, ChoiceQ, NoulQ, Question, ScoreQ

JEV_PRICE_PER_MTOK_INPUT = 0.042  # vendor list price (USD); output tokens free


@dataclass
class BackendResult:
    answers: dict[str, Answer]
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class DecisionBackend(Protocol):
    name: str

    def decide(self, state: str, questions: dict[str, Question]) -> BackendResult: ...


class JevBackend:
    name = "jev"

    def __init__(self, model: str | None = None) -> None:
        from typesafe_sdk import TypeSafeClient  # imported lazily so tests run without the SDK

        self._client = TypeSafeClient(model=model)  # reads TYPESAFE_API_KEY from env

    @staticmethod
    def _to_sdk(q: Question):
        from typesafe_sdk import Choice, Noul, Score

        if isinstance(q, ChoiceQ):
            return Choice(instructions=q.instructions, criteria=dict(q.criteria))
        if isinstance(q, ScoreQ):
            return Score(instructions=q.instructions, criteria=list(q.levels))
        if isinstance(q, NoulQ):
            return Noul(instructions=q.instructions)
        raise TypeError(f"Unsupported question type: {type(q)}")

    def decide(self, state: str, questions: dict[str, Question]) -> BackendResult:
        resp = self._client.system_one(
            state=state, questions={k: self._to_sdk(q) for k, q in questions.items()}
        )
        answers: dict[str, Answer] = {}
        for name, a in resp.answers.items():
            if a.type == "choice":
                answers[name] = Answer("choice", a.choice, dict(a.probabilities), a.confidence)
            elif a.type == "score":
                probs = {str(k): v for k, v in a.probabilities.items()}
                answers[name] = Answer("score", int(a.score), probs, a.confidence)
            else:
                answers[name] = Answer("noul", float(a.noul))
        tokens_in = resp.usage.input_tokens or 0
        return BackendResult(
            answers=answers,
            model=resp.model,
            input_tokens=tokens_in,
            output_tokens=resp.usage.output_tokens or 0,
            cost_usd=tokens_in / 1e6 * JEV_PRICE_PER_MTOK_INPUT,
        )


class RulesBackend:
    """Keyword baseline. Answers Choice questions only; abstains (None) on everything else."""

    name = "rules"

    def __init__(self, keywords: dict[str, dict[str, list[str]]]) -> None:
        # question name -> option -> keywords
        self._kw = {
            q: {opt: [re.compile(rf"\b{re.escape(w)}", re.I) for w in words] for opt, words in opts.items()}
            for q, opts in keywords.items()
        }

    def decide(self, state: str, questions: dict[str, Question]) -> BackendResult:
        answers: dict[str, Answer] = {}
        for name, q in questions.items():
            if isinstance(q, ChoiceQ) and name in self._kw:
                hits = {opt: sum(len(p.findall(state)) for p in pats) for opt, pats in self._kw[name].items()}
                total = sum(hits.values())
                if total == 0:
                    answers[name] = Answer("choice", None, {}, 0.0)
                    continue
                probs = {opt: h / total for opt, h in hits.items()}
                best = max(probs, key=probs.get)
                answers[name] = Answer("choice", best, probs, None)
            else:
                answers[name] = Answer(q.__class__.__name__.lower().removesuffix("q"), None)
        return BackendResult(answers=answers, model="rules-v1")
