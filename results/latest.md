# Triage evaluation — 2026-10-08T20:20:32+00:00

Model: `jev-1.13.0` · Cases: **500**

> CFPB product labels are chosen by consumers when filing; treated as a noisy proxy for truth.

## Headline
- Product accuracy: **74.4%** (95% CI 70.4%–78.0%)
- ECE raw: **0.179** → recalibrated (cross-fitted): **0.088**
- Safe auto-threshold (raw): **none** reaches the 95.0% lower-bound target
- Safe auto-threshold (recalibrated): **none** reaches the 95.0% lower-bound target
- **Routing group (ADR-007)** accuracy: **87.4%** · ECE raw 0.081 → recalibrated 0.062
- Routing safe auto-threshold (recalibrated): **none** reaches the target
- Risk flag rates: alleged_deception 22.0%, alleged_discrimination 0.8%, threats_or_harassment 6.6%
- Keyword baseline: accuracy 55.0%, coverage 83.2%
- Latency p50/p95: 111 / 149 ms · cost/case $0.000051

## Reliability (raw)

| bin | n | mean p | accuracy |
|---|---|---|---|
| 0.3–0.4 | 1 | 0.38 | 1.00 |
| 0.4–0.5 | 9 | 0.46 | 0.22 |
| 0.5–0.6 | 19 | 0.56 | 0.32 |
| 0.6–0.7 | 24 | 0.65 | 0.54 |
| 0.7–0.8 | 32 | 0.76 | 0.59 |
| 0.8–0.9 | 36 | 0.85 | 0.56 |
| 0.9–1.0 | 379 | 0.99 | 0.82 |

## Top confusions (label → predicted)

- debt_collection → credit_reporting: 39
- bank_account → credit_card: 12
- bank_account → money_transfer: 10
- money_transfer → bank_account: 6
- credit_card → bank_account: 5
- personal_loan → debt_collection: 4
- credit_card → personal_loan: 4
- debt_collection → credit_card: 4
