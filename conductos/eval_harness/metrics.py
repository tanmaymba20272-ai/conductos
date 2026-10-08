"""Statistics for calibration and autonomy thresholds (PRD-C §7.2).

Key idea: a threshold is only safe if the *lower* 95% confidence bound of precision above it
meets the target. Point estimates on small samples are how teams talk themselves into risk.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def reliability_bins(p: np.ndarray, correct: np.ndarray, n_bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 1, n_bins + 1)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        n = int(mask.sum())
        out.append({
            "lo": round(float(lo), 2), "hi": round(float(hi), 2), "n": n,
            "mean_p": float(p[mask].mean()) if n else None,
            "accuracy": float(correct[mask].mean()) if n else None,
        })
    return out


def ece(p: np.ndarray, correct: np.ndarray, n_bins: int = 10) -> float:
    total = len(p)
    if total == 0:
        return float("nan")
    return float(sum(
        b["n"] / total * abs(b["mean_p"] - b["accuracy"])
        for b in reliability_bins(p, correct, n_bins) if b["n"]
    ))


def brier_multiclass(prob_dicts: list[dict[str, float]], labels: list[str]) -> float:
    scores = []
    for probs, y in zip(prob_dicts, labels):
        scores.append(sum((v - (1.0 if k == y else 0.0)) ** 2 for k, v in probs.items()))
    return float(np.mean(scores)) if scores else float("nan")


@dataclass
class ThresholdPoint:
    threshold: float
    coverage: float
    n: int
    precision: float
    precision_lower: float


def coverage_precision_curve(p: np.ndarray, correct: np.ndarray) -> list[ThresholdPoint]:
    order = np.argsort(-p)
    ps, cs = p[order], correct[order]
    total = len(p)
    points: list[ThresholdPoint] = []
    k = 0
    for i in range(total):
        k += int(cs[i])
        # only emit at distinct threshold values
        if i + 1 < total and ps[i + 1] == ps[i]:
            continue
        n = i + 1
        points.append(ThresholdPoint(
            threshold=float(ps[i]), coverage=n / total, n=n,
            precision=k / n, precision_lower=wilson_interval(k, n)[0],
        ))
    return points


def pick_threshold(p: np.ndarray, correct: np.ndarray, target: float = 0.95, min_n: int = 30) -> ThresholdPoint | None:
    """Lowest threshold (max coverage) whose precision lower bound meets the target."""
    ok = [pt for pt in coverage_precision_curve(p, correct) if pt.n >= min_n and pt.precision_lower >= target]
    return max(ok, key=lambda pt: pt.coverage) if ok else None


class IsotonicCalibrator:
    """Pool-adjacent-violators isotonic regression mapping raw p -> P(correct)."""

    def fit(self, p: np.ndarray, correct: np.ndarray) -> "IsotonicCalibrator":
        order = np.argsort(p)
        x, y = p[order].astype(float), correct[order].astype(float)
        blocks = [[yi, 1.0, xi, xi] for xi, yi in zip(x, y)]  # [sum_y, weight, x_min, x_max]
        merged: list[list[float]] = []
        for b in blocks:
            merged.append(b)
            while len(merged) > 1 and merged[-2][0] / merged[-2][1] > merged[-1][0] / merged[-1][1]:
                b2 = merged.pop()
                b1 = merged.pop()
                merged.append([b1[0] + b2[0], b1[1] + b2[1], b1[2], b2[3]])
        self.x_ = np.array([(b[2] + b[3]) / 2 for b in merged])
        self.y_ = np.array([b[0] / b[1] for b in merged])
        return self

    def __call__(self, p: float) -> float:
        return float(np.interp(p, self.x_, self.y_))

    def predict(self, p: np.ndarray) -> np.ndarray:
        return np.interp(p, self.x_, self.y_)


def cross_fitted_calibration(p: np.ndarray, correct: np.ndarray, k: int = 5, seed: int = 7) -> np.ndarray:
    """Out-of-fold calibrated probabilities, so we never evaluate a calibrator on its own training data."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(p))
    out = np.empty(len(p))
    for fold in np.array_split(idx, k):
        train = np.setdiff1d(idx, fold)
        out[fold] = IsotonicCalibrator().fit(p[train], correct[train]).predict(p[fold])
    return out


def percentile(xs: list[float], q: float) -> float | None:
    return float(np.percentile(xs, q)) if xs else None
