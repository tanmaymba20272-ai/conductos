"""Triage evaluation report under the pre-registered protocol (ADR-008).

Calibrator and auto-routing threshold are fitted on the tune half only. Development runs report the
tune half (with tune-only error examples). A final run also reveals the test half, scored with the
tune-fitted calibrator and threshold; that is the published result.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

import numpy as np

from conductos.data.taxonomy import SUB_TEAMS, business_line_probabilities
from conductos.eval_harness import metrics as m


def _side(p: np.ndarray, correct: np.ndarray, calibrator: m.IsotonicCalibrator | None) -> dict:
    n, k = len(p), int(correct.sum())
    p_cal = calibrator.predict(p) if calibrator else p
    return {
        "n": n,
        "accuracy": {"value": k / n if n else None, "ci95": m.wilson_interval(k, n)},
        "calibration": {
            "raw": {"ece": m.ece(p, correct), "bins": m.reliability_bins(p, correct)},
            "recalibrated": {"ece": m.ece(p_cal, correct), "bins": m.reliability_bins(p_cal, correct)},
        },
    }


def _level(p: np.ndarray, correct: np.ndarray, is_tune: np.ndarray, target: float, reveal_test: bool) -> tuple[dict, m.IsotonicCalibrator | None]:
    p_t, c_t = p[is_tune], correct[is_tune]
    cal = m.IsotonicCalibrator().fit(p_t, c_t) if len(p_t) >= 50 else None
    tune = _side(p_t, c_t, None)
    # within the tune half, report honest (out-of-fold) recalibration, not the in-sample fit
    p_t_cf = m.cross_fitted_calibration(p_t, c_t) if len(p_t) >= 50 else p_t
    tune["calibration"]["recalibrated"] = {"ece": m.ece(p_t_cf, c_t), "bins": m.reliability_bins(p_t_cf, c_t)}
    th = m.pick_threshold(cal.predict(p_t) if cal else p_t, c_t, target)
    tune["threshold"] = _pt(th)
    block = {"target_precision_lower_bound": target, "tune": tune}
    if reveal_test:
        p_s, c_s = p[~is_tune], correct[~is_tune]
        test = _side(p_s, c_s, cal)
        if th is not None:
            above = (cal.predict(p_s) if cal else p_s) >= th.threshold
            k, n = int(c_s[above].sum()), int(above.sum())
            lo = m.wilson_interval(k, n)[0] if n else 0.0
            test["at_threshold"] = {"threshold": th.threshold, "coverage": n / len(p_s) if len(p_s) else 0.0, "n": n,
                                    "precision": k / n if n else None, "precision_lower": lo,
                                    "passes": bool(n and lo >= target)}
        else:
            test["at_threshold"] = None
        block["test"] = test
    return block, cal


def evaluate(records: list[dict], baseline: list[dict] | None = None, target: float = 0.95,
             reveal_test: bool = False) -> dict:
    """records: [{case_id, label (sub-team), split, sub_team, sub_team_probabilities, narrative_head,
    severity, vulnerable_p, regulatory_risk_p, risk_flags, injection_p, latency_ms, cost_usd, model, backend}]"""
    scored = [r for r in records if r.get("sub_team_probabilities")]
    rec = [r for r in scored if r.get("label")]  # primary answer key: human labels (ADR-008 amendment 1)
    is_tune = np.array([r["split"] == "tune" for r in rec])
    labels = [r["label"] for r in rec]
    preds = [r["sub_team"] for r in rec]
    p = np.array([max(r["sub_team_probabilities"].values()) for r in rec])
    correct = np.array([a == b for a, b in zip(preds, labels)], dtype=float)
    sub_team, calibrator = _level(p, correct, is_tune, target, reveal_test)

    lprobs = [business_line_probabilities(r["sub_team_probabilities"]) for r in rec]
    l_pred = [max(x, key=x.get) for x in lprobs]
    l_correct = np.array([lp == SUB_TEAMS[y][0] for lp, y in zip(l_pred, labels)], dtype=float)
    business_line, _ = _level(np.array([max(x.values()) for x in lprobs]), l_correct, is_tune, target, reveal_test)

    shown = ~is_tune if reveal_test else is_tune  # the split whose details are reported
    idx = [i for i in range(len(rec)) if shown[i]]
    per_team = {}
    for t in SUB_TEAMS:
        tp = sum(1 for i in idx if preds[i] == t and labels[i] == t)
        fp = sum(1 for i in idx if preds[i] == t and labels[i] != t)
        fn = sum(1 for i in idx if preds[i] != t and labels[i] == t)
        per_team[t] = {"line": SUB_TEAMS[t][0], "support": tp + fn,
                       "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None,
                       "judged": tp + fn >= 30}

    tune_idx = [i for i in range(len(rec)) if is_tune[i]]
    confusions = Counter((labels[i], preds[i]) for i in tune_idx if labels[i] != preds[i]).most_common(10)
    errors = [i for i in tune_idx if labels[i] != preds[i]]
    errors.sort(key=lambda i: -p[i])  # most confident mistakes first
    examples = [{"split": "tune", "label": labels[i], "predicted": preds[i], "p": round(float(p[i]), 3),
                 "narrative_head": rec[i].get("narrative_head", "")} for i in errors[:25]]

    srec = [rec[i] for i in idx]

    def flag_rate(key: str) -> float | None:
        vals = [r[key] for r in srec if r.get(key) is not None]
        return float(np.mean([v >= 0.5 for v in vals])) if vals else None

    lat = [r["latency_ms"] for r in rec if r.get("latency_ms") is not None]
    cost = [r["cost_usd"] for r in rec if r.get("cost_usd") is not None]
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": rec[0]["model"] if rec else None,
        "evaluated_split": "test" if reveal_test else "tune",
        "n_total": len(scored),
        "n_human_labeled": len(rec),
        "label_caveat": "Primary answer key = blind human labels (one labeler). Secondary = written rules on consumer-chosen CFPB fields.",
        "sub_team": sub_team,
        "business_line": business_line,
        "calibrator": {"fit_on": "tune", "x": calibrator.x_.tolist(), "y": calibrator.y_.tolist()} if calibrator else None,
        "per_sub_team": per_team,
        "tune_confusions": [{"label": l, "predicted": q, "count": c} for (l, q), c in confusions],
        "tune_error_examples": examples,
        "signals": {
            "severity_distribution": dict(Counter(str(r.get("severity")) for r in srec)),
            "vulnerable_flag_rate": flag_rate("vulnerable_p"),
            "regulatory_risk_flag_rate": flag_rate("regulatory_risk_p"),
            "risk_flag_rates": {
                f: float(np.mean([r["risk_flags"][f] >= 0.5 for r in srec if f in r.get("risk_flags", {})]))
                for f in sorted({f for r in srec for f in r.get("risk_flags", {})})
            },
            "injection_flag_rate": flag_rate("injection_p"),
            "note": "Severity and risk flags have no ground-truth labels yet; distributions only.",
        },
        "ops": {
            "latency_ms_p50": m.percentile(lat, 50),
            "latency_ms_p95": m.percentile(lat, 95),
            "cost_usd_total": float(sum(cost)),
            "cost_usd_per_case": float(np.mean(cost)) if cost else None,
        },
    }
    # secondary answer key: CFPB-rule labels on every scored complaint in the reported split
    side = [r for r in scored if (r["split"] == "test") == reveal_test and r.get("rule_label")]
    result["cfpb_rule_key"] = {
        "n": len(side),
        "sub_team_accuracy": float(np.mean([r["sub_team"] == r["rule_label"] for r in side])) if side else None,
        "business_line_accuracy": float(np.mean([
            max(business_line_probabilities(r["sub_team_probabilities"]).items(), key=lambda kv: kv[1])[0]
            == SUB_TEAMS[r["rule_label"]][0] for r in side])) if side else None,
    }
    if baseline:
        keep = {rec[i]["case_id"] for i in idx}
        b = [x for x in baseline if x["case_id"] in keep]
        answered = [x for x in b if x.get("sub_team")]
        bk = sum(1 for x in answered if x["sub_team"] == x["label"])
        result["baseline_rules"] = {
            "coverage": len(answered) / len(b) if b else None,
            "accuracy_all": bk / len(b) if b else None,
            "accuracy_when_answered": bk / len(answered) if answered else None,
        }
    return result


def _pt(pt: m.ThresholdPoint | None) -> dict | None:
    if pt is None:
        return None
    return {"threshold": pt.threshold, "coverage": pt.coverage, "n": pt.n,
            "precision": pt.precision, "precision_lower": pt.precision_lower}


def to_markdown(r: dict) -> str:
    def pct(x):
        return "n/a" if x is None else f"{x*100:.1f}%"

    split = r["evaluated_split"]
    lines = [
        f"# Triage evaluation — {r['generated_at']}",
        "",
        f"Model: `{r['model']}` · Complaints: **{r['n_total']}** (human-labeled: {r['n_human_labeled']}) · Reported split: **{split}**"
        + ("" if split == "test" else " (development run; test half not revealed)"),
        "",
        f"> {r['label_caveat']}",
        "",
    ]
    for level, title in (("sub_team", "Sub-team"), ("business_line", "Business line")):
        b = r[level]
        side = b[split]
        cal = side["calibration"]
        lines += [
            f"## {title}",
            f"- Accuracy ({split}): **{pct(side['accuracy']['value'])}** (95% CI {pct(side['accuracy']['ci95'][0])}–{pct(side['accuracy']['ci95'][1])})",
            f"- Calibration error ({split}): raw {cal['raw']['ece']:.3f} → recalibrated {cal['recalibrated']['ece']:.3f}",
        ]
        th = b["tune"]["threshold"]
        lines.append("- Threshold chosen on tune: " + (
            f"p ≥ {th['threshold']:.3f} (tune coverage {pct(th['coverage'])}, lower bound {pct(th['precision_lower'])})"
            if th else f"**none** reaches {pct(b['target_precision_lower_bound'])} on the tune half"))
        if split == "test":
            at = side["at_threshold"]
            lines.append("- **Test at that threshold:** " + (
                f"coverage {pct(at['coverage'])}, precision {pct(at['precision'])}, lower bound {pct(at['precision_lower'])} → "
                + ("**passes**" if at["passes"] else "**does not pass**") if at else "no threshold to test"))
        lines.append("")
    ck = r["cfpb_rule_key"]
    lines.append(f"Secondary key (CFPB rules, {ck['n']} {split} complaints): sub-team {pct(ck['sub_team_accuracy'])}, business line {pct(ck['business_line_accuracy'])}")
    if "baseline_rules" in r:
        lines.append(f"Keyword baseline ({split}): accuracy {pct(r['baseline_rules']['accuracy_all'])}")
    o = r["ops"]
    if o["latency_ms_p50"] is not None:
        lines.append(f"Latency p50/p95: {o['latency_ms_p50']:.0f} / {o['latency_ms_p95']:.0f} ms · cost/case ${o['cost_usd_per_case']:.6f}")
    lines += ["", f"## Per sub-team ({split})", "", "| sub-team | line | support | precision | recall |", "|---|---|---|---|---|"]
    for t, v in sorted(r["per_sub_team"].items(), key=lambda kv: -kv[1]["support"]):
        note = "" if v["judged"] else " (too few to judge)"
        lines.append(f"| {t}{note} | {v['line']} | {v['support']} | {pct(v['precision'])} | {pct(v['recall'])} |")
    lines += ["", "## Tune-half confusions (label → predicted)", ""]
    lines += [f"- {c['label']} → {c['predicted']}: {c['count']}" for c in r["tune_confusions"]]
    lines += ["", "## Tune-half error examples (most confident first)", ""]
    for e in r["tune_error_examples"]:
        lines.append(f"- **{e['label']} → {e['predicted']}** (p {e['p']}): {e['narrative_head'][:300]}")
    return "\n".join(lines) + "\n"
