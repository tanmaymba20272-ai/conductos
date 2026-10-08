import numpy as np
import pytest

from conductos.data.cfpb import parse, _rows
from conductos.eval_harness import metrics as m
from conductos.eval_harness.report import evaluate, to_markdown
from conductos.gateway import Gateway
from conductos.gateway.backends import BackendResult, RulesBackend
from conductos.gateway.questions import Answer, ChoiceQ
from conductos.gateway.redaction import redact
from conductos.ops_pod.contracts import Route, TriageDecision
from conductos.ops_pod.state_machine import Case, IllegalTransition, State
from conductos.ops_pod.supervisor import load_policy, route
from conductos.ops_pod.triage import RULES_KEYWORDS, TRIAGE_QUESTIONS


# ---------- data ----------
def test_cfpb_parse_handles_both_shapes_and_drops_unusable():
    rows = [
        {"complaint_id": 1, "product": "Mortgage", "complaint_what_happened": "Escrow wrong", "date_received": "2025-02-01T00:00:00"},
        {"complaint_id": 2, "product": "Mortgage", "complaint_what_happened": ""},  # no narrative
        {"complaint_id": 3, "product": "Unknown thing", "complaint_what_happened": "x"},  # unmapped
    ]
    es = {"hits": {"hits": [{"_source": r} for r in rows]}}
    for payload in (rows, es):
        out = parse(_rows(payload))
        assert [c.complaint_id for c in out] == ["1"]
        assert out[0].product_label == "mortgage"
        assert out[0].date_received == "2025-02-01"


# ---------- gateway ----------
def test_redaction():
    text, n = redact("Email me at a.b@x.com or 555-123-4567, card 4111 1111 1111 1111")
    assert "[EMAIL]" in text and "[PHONE]" in text and "[CARD]" in text and n == 3


class Boom:
    name = "boom"

    def decide(self, state, questions):
        raise TimeoutError()


def test_gateway_falls_back_and_traces():
    gw = Gateway(chain=[Boom(), RulesBackend(RULES_KEYWORDS)])
    d = gw.decide("My mortgage escrow is wrong", {"product": TRIAGE_QUESTIONS["product"]})
    assert d.backend == "rules" and d.fallback_used
    assert d.result.answers["product"].value == "mortgage"
    assert gw.traces[0]["errors"] == ["boom: TimeoutError"]


def test_kill_switch():
    gw = Gateway(chain=[RulesBackend(RULES_KEYWORDS)])
    gw.kill()
    with pytest.raises(RuntimeError):
        gw.decide("x", {"product": TRIAGE_QUESTIONS["product"]})


def test_choice_limit():
    with pytest.raises(ValueError):
        ChoiceQ("q", {str(i): "x" for i in range(256)})


# ---------- ops pod ----------
def test_state_machine_blocks_illegal_transition():
    c = Case("1")
    with pytest.raises(IllegalTransition):
        c.transition(State.RESOLVED, "skip everything")
    c.transition(State.TRIAGED, "ok")
    c.transition(State.AUTO_RESOLVED, "ok")
    with pytest.raises(IllegalTransition):
        c.transition(State.HUMAN_REVIEW, "terminal")


def _t(**kw):
    base = dict(case_id="1", trace_id="t", model="m", backend="jev", product="mortgage",
                product_probabilities={"mortgage": 0.97, "bank_account": 0.03}, severity=1,
                vulnerable_p=0.1, regulatory_risk_p=0.1, injection_p=0.0, latency_ms=1, cost_usd=0)
    base.update(kw)
    return TriageDecision(**base)


def test_supervisor_routes():
    policy = load_policy()
    # no calibrated threshold published -> review, never auto
    assert route(_t(), policy).route == Route.REVIEW
    assert route(_t(injection_p=0.9), policy).route == Route.QUARANTINE
    assert "vulnerable-customer signal" in route(_t(vulnerable_p=0.8), policy).reasons
    policy["thresholds"]["product"] = {"auto": 0.9, "review": 0.6}
    ident = lambda p: p  # noqa: E731
    assert route(_t(), policy, ident).route == Route.AUTO
    assert route(_t(product_probabilities={"mortgage": 0.7, "x": 0.3}), policy, ident).route == Route.REVIEW
    assert route(_t(product_probabilities={"mortgage": 0.5, "x": 0.5}), policy, ident).route == Route.INVESTIGATE
    # mandatory review beats high confidence
    assert route(_t(severity=3), policy, ident).route == Route.REVIEW


# ---------- harness ----------
def test_wilson():
    lo, hi = m.wilson_interval(95, 100)
    assert 0.88 < lo < 0.90 and 0.97 < hi < 0.99


def test_isotonic_is_monotone_and_fixes_overconfidence():
    rng = np.random.default_rng(0)
    p = rng.uniform(0.5, 1.0, 4000)
    correct = (rng.uniform(size=4000) < (p - 0.2)).astype(float)  # model overconfident by 0.2
    cal = m.cross_fitted_calibration(p, correct)
    assert m.ece(p, correct) > 0.15
    assert m.ece(cal, correct) < 0.05
    iso = m.IsotonicCalibrator().fit(p, correct)
    assert np.all(np.diff(iso.y_) >= -1e-12)


def test_threshold_uses_lower_bound():
    p = np.array([0.99] * 20 + [0.6] * 80)
    correct = np.array([1.0] * 20 + [0.5 > i % 2 for i in range(80)], dtype=float)
    # 20/20 correct but lower bound < 0.95 at n=20 -> no safe threshold with min_n=30
    assert m.pick_threshold(p, correct, 0.95, min_n=30) is None


def test_evaluate_end_to_end_with_simulated_model():
    rng = np.random.default_rng(1)
    labels = ["mortgage", "credit_card", "debt_collection"]
    records = []
    for i in range(300):
        y = labels[i % 3]
        conf = rng.uniform(0.4, 1.0)
        right = rng.uniform() < conf - 0.1
        pred = y if right else labels[(i + 1) % 3]
        probs = {l: (conf if l == pred else (1 - conf) / 2) for l in labels}
        records.append(dict(case_id=str(i), label=y, product=pred, product_probabilities=probs,
                            severity=1, vulnerable_p=0.1, regulatory_risk_p=0.2, injection_p=0.0,
                            latency_ms=120.0, cost_usd=0.00002, model="sim", backend="sim"))
    r = evaluate(records)
    assert r["n"] == 300
    assert r["calibration"]["recalibrated_cross_fitted"]["ece"] < r["calibration"]["raw"]["ece"]
    assert "Triage evaluation" in to_markdown(r)
