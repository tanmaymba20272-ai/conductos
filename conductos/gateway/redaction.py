"""PII redaction applied before any text leaves the platform (Policy: input guardrail).

CFPB narratives are already scrubbed (XXXX), but the gateway never relies on upstream
cleaning: every call is redacted again, and the count is traced.
"""

from __future__ import annotations

import re

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("PHONE", re.compile(r"(?:\+?1[ .-]?)?\(?\b\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}\b")),
    ("ACCOUNT", re.compile(r"\b(?:acct|account)\s*(?:no\.?|number|#)?\s*:?\s*\d{6,}\b", re.I)),
]


def redact(text: str) -> tuple[str, int]:
    """Return (redacted_text, number_of_redactions)."""
    total = 0
    for label, pattern in _PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        total += n
    return text, total
