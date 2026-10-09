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
    d = gw.decide("My mortgage escrow is wrong", {"sub_team": TRIAGE_QUESTIONS["sub_team"]})
    assert d.backend == "rules" and d.fallback_used
    assert d.result.answers["sub_team"].value == "hl_servicing_escrow"
    assert gw.traces[0]["errors"] == ["boom: TimeoutError"]


def test_kill_switch():
    gw = Gateway(chain=[RulesBackend(RULES_KEYWORDS)])
    gw.kill()
    with pytest.raises(RuntimeError):
        gw.decide("x", {"sub_team": TRIAGE_QUESTIONS["sub_team"]})


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
    base = dict(case_id="1", trace_id="t", model="m", backend="jev", sub_team="hl_servicing_escrow",
                sub_team_probabilities={"hl_servicing_escrow": 0.97, "ca_card_disputes": 0.03}, severity=1,
                vulnerable_p=0.1, regulatory_risk_p=0.1, injection_p=0.0, latency_ms=1, cost_usd=0)
    base.update(kw)
    return TriageDecision(**base)


def test_supervisor_routes():
    policy = load_policy()
    # no calibrated threshold published -> review, never auto
    assert route(_t(), policy).route == Route.REVIEW
    # assist mode (ADR-009): the reviewer sees Jev's suggested team to confirm or correct
    assert route(_t(), policy).suggested_sub_team == "hl_servicing_escrow"
    assert route(_t(injection_p=0.9), policy).route == Route.QUARANTINE
    assert route(_t(injection_p=0.9), policy).suggested_sub_team is None  # quarantined text gets no suggestion
    assert "vulnerable-customer signal" in route(_t(vulnerable_p=0.8), policy).reasons
    policy["thresholds"]["sub_team"] = {"auto": 0.9, "review": 0.6}
    ident = lambda p: p  # noqa: E731
    assert route(_t(), policy, ident).route == Route.AUTO
    assert route(_t(sub_team_probabilities={"hl_servicing_escrow": 0.7, "ca_card_disputes": 0.3}), policy, ident).route == Route.REVIEW
    r = route(_t(sub_team_probabilities={"hl_servicing_escrow": 0.5, "ca_card_disputes": 0.5}), policy, ident)
    assert r.route == Route.INVESTIGATE and r.calibrated_routing_p == 0.5
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
    teams = ["cb_account_servicing", "cb_fraud_disputes", "ca_card_disputes", "hl_servicing_escrow"]
    records = []
    for i in range(400):
        y = teams[i % 4]
        conf = rng.uniform(0.4, 1.0)
        pred = y if rng.uniform() < conf - 0.1 else teams[(i + 1) % 4]
        probs = {t: (conf if t == pred else (1 - conf) / 3) for t in teams}
        records.append(dict(case_id=str(i), label=y if i < 300 else None, rule_label=y,  # last 100 unlabeled by humans
                            split="tune" if i % 2 else "test", sub_team=pred,
                            sub_team_probabilities=probs, narrative_head="text", severity=1, vulnerable_p=0.1,
                            regulatory_risk_p=0.2, injection_p=0.0, latency_ms=120.0, cost_usd=0.00002,
                            model="sim", backend="sim"))
    dev = evaluate(records)
    assert dev["evaluated_split"] == "tune" and "test" not in dev["sub_team"]
    assert dev["tune_error_examples"] and all(e["split"] == "tune" for e in dev["tune_error_examples"])
    final = evaluate(records, reveal_test=True)
    assert final["evaluated_split"] == "test" and final["sub_team"]["test"]["n"] == 150  # human-labeled test only
    assert final["cfpb_rule_key"]["n"] == 200  # secondary key covers every test complaint
    assert final["business_line"]["test"]["accuracy"]["value"] >= final["sub_team"]["test"]["accuracy"]["value"]
    assert "Claude" not in dev["label_caveat"]
    records[1]["labeler"] = "Claude (applying labeler's rules)"  # record 1 is in the tune half
    assert "149 human-labeled, 1 labeled by Claude" in evaluate(records)["label_caveat"]
    assert final["calibrator"] and "Triage evaluation" in to_markdown(final)




def test_archive_sampling_from_csv_export(tmp_path):
    import csv, io, zipfile
    from conductos.data.cfpb import sample_archive

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Date received", "Product", "Sub-product", "Issue", "Sub-issue",
                "Consumer complaint narrative", "Company", "State", "Company response to consumer", "Complaint ID"])
    for i in range(50):
        narrative = "" if i % 5 == 0 else f"My escrow payment was wrong, case {i}"
        product = "Mortgage" if i % 7 else "Something unmapped"
        w.writerow(["2026-07-15", product, "", "Escrow", "", narrative, "BANK", "NY", "Closed", str(1000 + i)])
    z = tmp_path / "export.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("complaints.csv", buf.getvalue())

    a, stats = sample_archive([z], n=10, seed=1)
    b, _ = sample_archive([z], n=10, seed=1)
    assert len(a) == 10 and [c.complaint_id for c in a] == [c.complaint_id for c in b]  # reproducible
    assert all(c.narrative and c.product_label == "mortgage" for c in a)
    assert stats["rows"] == 50 and stats["usable"] < 50


def test_business_line_probabilities_sum_sub_teams():
    from conductos.data.taxonomy import business_line_probabilities

    b = business_line_probabilities({"cb_fraud_disputes": 0.5, "cb_fees_overdraft": 0.3, "ca_card_disputes": 0.2})
    assert abs(b["Consumer Banking"] - 0.8) < 1e-9 and abs(sum(b.values()) - 1) < 1e-9


def test_triage_with_rules_backend_handles_unanswered_flags():
    from conductos.ops_pod.contracts import CleanCase
    from conductos.ops_pod.triage import triage

    gw = Gateway(chain=[RulesBackend(RULES_KEYWORDS)])
    t = triage(CleanCase(case_id="1", text="My mortgage escrow is wrong", received="2026-07-01"), gw)
    assert t.sub_team == "hl_servicing_escrow" and t.regulatory_risk_p is None and t.risk_flags == {}


def test_survey_counts_narratives_by_company(tmp_path):
    import csv, io, zipfile
    from conductos.data.cfpb import survey

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Product", "Consumer complaint narrative", "Company", "Complaint ID"])
    w.writerow(["Credit card", "story", "BIG BANK, N.A.", "1"])
    w.writerow(["Credit card", "", "BIG BANK, N.A.", "2"])  # no narrative: not counted
    w.writerow(["Mortgage", "story", "SMALL CO", "3"])
    z = tmp_path / "e.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("c.csv", buf.getvalue())
    s = survey(z)
    assert s["rows"] == 3 and s["with_narrative"] == 2
    assert s["companies"]["BIG BANK, N.A."] == 1 and s["companies"]["SMALL CO"] == 1


def test_bank_sample_filters_companies_across_exports_and_splits(tmp_path):
    import csv, io, zipfile
    import pytest
    from conductos.data.cfpb import sample_archive

    def export(name, start):
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Product", "Consumer complaint narrative", "Company", "Complaint ID"])
        for i in range(start, start + 30):
            w.writerow(["Credit card", f"story {i}", "BIG BANK, N.A." if i % 2 else "COLLECTOR LLC", str(i)])
        z = tmp_path / name
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr("c.csv", buf.getvalue())
        return z

    zips = [export("a.zip", 0), export("b.zip", 100)]
    out, stats = sample_archive(zips, n=20, seed=3, companies={"BIG BANK, N.A."})
    assert len(out) == 20 and all(c.company == "BIG BANK, N.A." for c in out)
    assert stats["usable"] == 30  # 15 bank rows per export
    assert sum(c.split == "tune" for c in out) == 10 and sum(c.split == "test" for c in out) == 10
    with pytest.raises(RuntimeError, match="Only 30"):
        sample_archive(zips, n=40, seed=3, companies={"BIG BANK, N.A."})


def test_every_golden_complaint_maps_to_exactly_one_sub_team():
    import json
    from pathlib import Path
    from conductos.data.taxonomy import SUB_TEAMS, sub_team_for

    rows = [json.loads(x) for x in Path("data/golden/cfpb_sample.jsonl").read_text().splitlines()]
    assert len(rows) == 2000
    teams = [sub_team_for(r["cfpb_product"], r["cfpb_sub_product"], r["cfpb_issue"]) for r in rows]
    assert all(t in SUB_TEAMS for t in teams)
    assert {SUB_TEAMS[t][0] for t in SUB_TEAMS} == {"Consumer Banking", "Card Services & Auto", "Home Lending", "Shared"}
    assert len(SUB_TEAMS) == 15


def test_sub_team_rules():
    import pytest
    from conductos.data.taxonomy import sub_team_for

    assert sub_team_for("Credit card", "General-purpose credit card or charge card",
                        "Problem with a purchase shown on your statement") == "ca_card_disputes"
    assert sub_team_for("Credit card", "Store credit card", "Incorrect information on your report") == "sh_credit_bureau_disputes"
    assert sub_team_for("Debt collection", "I do not know", "Attempts to collect debt not owed") == "ca_collections_recoveries"
    assert sub_team_for("Debt collection", "Mortgage debt", "Written notification about debt") == "hl_loss_mitigation"
    assert sub_team_for("Payday loan, title loan, personal loan, or advance loan", "Installment loan",
                        "Getting the loan") == "ca_card_personal_loan_servicing"
    assert sub_team_for("Checking or savings account", "Checking account", "Closing an account") == "sh_closures_restrictions"
    # ADR-008 amendment 2, rule 1: card closures go to the shared closures team
    assert sub_team_for("Credit card", "General-purpose credit card or charge card", "Closing your account") == "sh_closures_restrictions"
    from conductos.data.taxonomy import SUB_TEAMS
    assert SUB_TEAMS["sh_closures_restrictions"][0] == "Shared"
    assert sub_team_for("Mortgage", "FHA mortgage", "Struggling to pay mortgage") == "hl_loss_mitigation"
    with pytest.raises(ValueError):
        sub_team_for("Some new product", None, None)
