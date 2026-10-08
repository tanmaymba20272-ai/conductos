# Triage evaluation — 2026-10-08T19:44:05+00:00

Model: `jev-1.13.0` · Cases: **500**

> CFPB product labels are chosen by consumers when filing; treated as a noisy proxy for truth.

## Headline
- Product accuracy: **74.8%** (95% CI 70.8%–78.4%)
- ECE raw: **0.172** → recalibrated (cross-fitted): **0.093**
- Safe auto-threshold (raw): **none** reaches the 95.0% lower-bound target
- Safe auto-threshold (recalibrated): **none** reaches the 95.0% lower-bound target
- Keyword baseline: accuracy 55.0%, coverage 83.2%
- Latency p50/p95: 133 / 180 ms · cost/case $0.000048

## Reliability (raw)

| bin | n | mean p | accuracy |
|---|---|---|---|
| 0.3–0.4 | 3 | 0.38 | 0.00 |
| 0.4–0.5 | 3 | 0.45 | 0.00 |
| 0.5–0.6 | 24 | 0.55 | 0.50 |
| 0.6–0.7 | 24 | 0.65 | 0.42 |
| 0.7–0.8 | 30 | 0.75 | 0.53 |
| 0.8–0.9 | 38 | 0.85 | 0.63 |
| 0.9–1.0 | 378 | 0.99 | 0.83 |

## Top confusions (label → predicted)

- debt_collection → credit_reporting: 39
- bank_account → credit_card: 11
- bank_account → money_transfer: 10
- money_transfer → bank_account: 6
- credit_card → bank_account: 5
- personal_loan → debt_collection: 4
- credit_card → personal_loan: 4
- debt_collection → credit_card: 3
