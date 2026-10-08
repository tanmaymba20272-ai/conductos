"""Build the triage evaluation report: raw vs recalibrated calibration, safe thresholds, baseline."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

import numpy as np

from conductos.data.taxonomy import GROUP_OF, group_probabilities
from conductos.eval_harness import metrics as m


def _decision_block(p_raw: np.ndarray, correct: np.ndarray, target: float) -> tuple[dict, m.IsotonicCalibrator | None]:
    """Accuracy, calibration (raw and cross-fitted recalibrated) and safe thresholds for one decision."""
    n, k = len(p_raw), int(correct.sum())
    p_cal = m.cross_fitted_calibration(p_raw, correct) if n >= 50 else p_raw
    th_raw = m.pick_threshold(p_raw, correct, target)
    th_cal = m.pick_threshold(p_cal, correct, target)
    block = {
        "n": n,
        "accuracy": {"value": k / n if n else None, "ci95": m.wilson_interval(k, n)},
        "calibration": {
            "raw": {"ece": m.ece(p_raw, correct), "bins": m.reliability_bins(p_raw, correct)},
            "recalibrated_cross_fitted": {"ece": m.ece(p_cal, correct), "bins": m.reliability_bins(p_cal, correct)},
        },
        "autonomy_threshold": {
            "target_precision_lower_bound": target,
            "raw": _pt(th_raw),
            "recalibrated": _pt(th_cal),
            "escalation_rate_at_recalibrated": (1 - th_cal.coverage) if th_cal else 1.0,
        },
    }
    return block, (m.IsotonicCalibrator().fit(p_raw, correct) if n >= 50 else None)


def evaluate(records: list[dict], baseline: list[dict] | None = None, target: float = 0.95) -> dict:
    """records: [{case_id, label, product, product_probabilities, severity, vulnerable_p,
    regulatory_risk_p, risk_flags, injection_p, latency_ms, cost_usd, model, backend}]"""
    rec = [r for r in records if r.get("product_probabilities")]
    labels = [r["label"] for r in rec]
    preds = [r["product"] for r in rec]
    p_raw = np.array([max(r["product_probabilities"].values()) for r in rec])
    correct = np.array([a == b for a, b in zip(preds, labels)], dtype=float)
    n = len(rec)
    product, _ = _decision_block(p_raw, correct, target)

    # ADR-007: routing decision on operational groups (sum of product probabilities)
    gprobs = [group_probabilities(r["product_probabilities"]) for r in rec]
    g_pred = [max(g, key=g.get) for g in gprobs]
    g_correct = np.array([gp == GROUP_OF[y] for gp, y in zip(g_pred, labels)], dtype=float)
    routing, routing_cal = _decision_block(np.array([max(g.values()) for g in gprobs]), g_correct, target)

    per_class = {}
    for c in sorted(set(labels) | set(preds)):
        tp = sum(1 for a, b in zip(preds, labels) if a == c and b == c)
        fp = sum(1 for a, b in zip(preds, labels) if a == c and b != c)
        fn = sum(1 for a, b in zip(preds, labels) if a != c and b == c)
        per_class[c] = {
            "support": tp + fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
        }

    confusions = Counter((b, a) for a, b in zip(preds, labels) if a != b).most_common(8)

    def flag_rate(key: str) -> float | None:
        vals = [r[key] for r in rec if r.get(key) is not None]
        return float(np.mean([v >= 0.5 for v in vals])) if vals else None

    lat = [r["latency_ms"] for r in rec if r.get("latency_ms") is not None]
    cost = [r["cost_usd"] for r in rec if r.get("cost_usd") is not None]

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": rec[0]["model"] if rec else None,
        "n": n,
        "label_caveat": "CFPB product labels are chosen by consumers when filing; treated as a noisy proxy for truth.",
        "accuracy": product["accuracy"],
        "calibration": {
            **product["calibration"],
            "raw": {**product["calibration"]["raw"],
                    "brier": m.brier_multiclass([r["product_probabilities"] for r in rec], labels)},
        },
        "autonomy_threshold": product["autonomy_threshold"],
        "routing": routing,
        "calibrator_for": "routing_group",
        "calibrator": {"x": routing_cal.x_.tolist(), "y": routing_cal.y_.tolist()} if routing_cal else None,
        "per_class": per_class,
        "top_confusions": [{"label": l, "predicted": p, "count": c} for (l, p), c in confusions],
        "signals": {
            "severity_distribution": dict(Counter(str(r.get("severity")) for r in rec)),
            "vulnerable_flag_rate": flag_rate("vulnerable_p"),
            "regulatory_risk_flag_rate": flag_rate("regulatory_risk_p"),
            "risk_flag_rates": {
                f: float(np.mean([r["risk_flags"][f] >= 0.5 for r in rec if f in r.get("risk_flags", {})]))
                for f in sorted({f for r in rec for f in r.get("risk_flags", {})})
            },
            "injection_flag_rate": flag_rate("injection_p"),
            "note": "Severity and risk flags have no ground-truth labels yet; distributions only (see Red-Team #1).",
        },
        "ops": {
            "latency_ms_p50": m.percentile(lat, 50),
            "latency_ms_p95": m.percentile(lat, 95),
            "cost_usd_total": float(sum(cost)),
            "cost_usd_per_case": float(np.mean(cost)) if cost else None,
        },
    }
    if baseline:
        b = [x for x in baseline if x["case_id"] in {r["case_id"] for r in rec}]
        answered = [x for x in b if x.get("product")]
        bk = sum(1 for x in answered if x["product"] == x["label"])
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

    acc = r["accuracy"]
    th = r["autonomy_threshold"]
    lines = [
        f"# Triage evaluation — {r['generated_at']}",
        "",
        f"Model: `{r['model']}` · Cases: **{r['n']}**",
        "",
        f"> {r['label_caveat']}",
        "",
        "## Headline",
        f"- Product accuracy: **{pct(acc['value'])}** (95% CI {pct(acc['ci95'][0])}–{pct(acc['ci95'][1])})",
        f"- ECE raw: **{r['calibration']['raw']['ece']:.3f}** → recalibrated (cross-fitted): **{r['calibration']['recalibrated_cross_fitted']['ece']:.3f}**",
    ]
    for name in ("raw", "recalibrated"):
        t = th[name]
        if t:
            lines.append(f"- Safe auto-threshold ({name}): p ≥ {t['threshold']:.3f} → coverage **{pct(t['coverage'])}**, precision {pct(t['precision'])} (lower bound {pct(t['precision_lower'])})")
        else:
            lines.append(f"- Safe auto-threshold ({name}): **none** reaches the {pct(th['target_precision_lower_bound'])} lower-bound target")
    if "routing" in r:
        rt = r["routing"]
        lines.append(f"- **Routing group (ADR-007)** accuracy: **{pct(rt['accuracy']['value'])}** · ECE raw {rt['calibration']['raw']['ece']:.3f} → recalibrated {rt['calibration']['recalibrated_cross_fitted']['ece']:.3f}")
        t = rt["autonomy_threshold"]["recalibrated"]
        lines.append(f"- Routing safe auto-threshold (recalibrated): " + (f"p ≥ {t['threshold']:.3f} → coverage **{pct(t['coverage'])}**, precision lower bound {pct(t['precision_lower'])}" if t else "**none** reaches the target"))
    if r["signals"].get("risk_flag_rates"):
        lines.append("- Risk flag rates: " + ", ".join(f"{k} {pct(v)}" for k, v in r["signals"]["risk_flag_rates"].items()))
    if "baseline_rules" in r:
        b = r["baseline_rules"]
        lines.append(f"- Keyword baseline: accuracy {pct(b['accuracy_all'])}, coverage {pct(b['coverage'])}")
    o = r["ops"]
    if o["latency_ms_p50"] is not None:
        lines.append(f"- Latency p50/p95: {o['latency_ms_p50']:.0f} / {o['latency_ms_p95']:.0f} ms · cost/case ${o['cost_usd_per_case']:.6f}")
    lines += ["", "## Reliability (raw)", "", "| bin | n | mean p | accuracy |", "|---|---|---|---|"]
    for b in r["calibration"]["raw"]["bins"]:
        if b["n"]:
            lines.append(f"| {b['lo']:.1f}–{b['hi']:.1f} | {b['n']} | {b['mean_p']:.2f} | {b['accuracy']:.2f} |")
    lines += ["", "## Top confusions (label → predicted)", ""]
    lines += [f"- {c['label']} → {c['predicted']}: {c['count']}" for c in r["top_confusions"]]
    return "\n".join(lines) + "\n"
