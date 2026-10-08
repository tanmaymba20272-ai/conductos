# Triage evaluation — 2026-10-08T22:28:09+00:00

Model: `jev-1.13.0` · Complaints: **2000** (human-labeled: 650) · Reported split: **tune** (development run; test half not revealed)

> Primary answer key = blind human labels (one labeler). Secondary = written rules on consumer-chosen CFPB fields.

## Sub-team
- Accuracy (tune): **77.3%** (95% CI 70.0%–83.3%)
- Calibration error (tune): raw 0.135 → recalibrated 0.080
- Threshold chosen on tune: **none** reaches 95.0% on the tune half

## Business line
- Accuracy (tune): **88.7%** (95% CI 82.6%–92.8%)
- Calibration error (tune): raw 0.055 → recalibrated 0.058
- Threshold chosen on tune: **none** reaches 95.0% on the tune half

Secondary key (CFPB rules, 1000 tune complaints): sub-team 51.2%, business line 76.6%
Keyword baseline (tune): accuracy 50.0%
Latency p50/p95: 132 / 172 ms · cost/case $0.000057

## Per sub-team (tune)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| cb_fraud_disputes | Consumer Banking | 30 | 65.0% | 86.7% |
| ca_card_disputes (too few to judge) | Card Services & Auto | 26 | 76.7% | 88.5% |
| ca_card_personal_loan_servicing (too few to judge) | Card Services & Auto | 23 | 100.0% | 65.2% |
| cb_closures_restrictions (too few to judge) | Consumer Banking | 13 | 64.3% | 69.2% |
| ca_collections_recoveries (too few to judge) | Card Services & Auto | 13 | 100.0% | 92.3% |
| cb_account_servicing (too few to judge) | Consumer Banking | 9 | 66.7% | 66.7% |
| sh_credit_bureau_disputes (too few to judge) | Shared | 7 | 66.7% | 85.7% |
| cb_fees_overdraft (too few to judge) | Consumer Banking | 6 | 100.0% | 83.3% |
| ca_card_applications (too few to judge) | Card Services & Auto | 6 | 100.0% | 50.0% |
| cb_opening_onboarding (too few to judge) | Consumer Banking | 4 | n/a | 0.0% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 4 | 75.0% | 75.0% |
| hl_servicing_escrow (too few to judge) | Home Lending | 3 | 100.0% | 66.7% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 2 | 100.0% | 100.0% |
| hl_loss_mitigation (too few to judge) | Home Lending | 2 | 66.7% | 100.0% |
| hl_origination (too few to judge) | Home Lending | 2 | 100.0% | 100.0% |

## Tune-half confusions (label → predicted)

- cb_fraud_disputes → ca_card_disputes: 4
- ca_card_applications → cb_fraud_disputes: 3
- ca_card_personal_loan_servicing → cb_closures_restrictions: 3
- ca_card_disputes → cb_fraud_disputes: 3
- cb_closures_restrictions → cb_fraud_disputes: 3
- ca_card_personal_loan_servicing → ca_card_disputes: 3
- cb_opening_onboarding → cb_fraud_disputes: 2
- cb_account_servicing → cb_closures_restrictions: 2
- ca_card_personal_loan_servicing → sh_credit_bureau_disputes: 2
- cb_opening_onboarding → cb_account_servicing: 2

## Tune-half error examples (most confident first)

- **cb_account_servicing → cb_fraud_disputes** (p 0.99): I suffered property loss or stolen in the amount of over {$250000.00} when Wells Fargo Bank merge with XXXX XXXX in XXXX. I rented a Safe Deposit Box form XXXX after XXXX XXXX of XXXX and in XXXX with XXXX XXXX XXXX arranged to pay for rental fees with automatic withdrawal over draft protection. XXX
- **cb_closures_restrictions → cb_fraud_disputes** (p 0.99): Wells Fargo notified me that my deposit accounts had been closed because they alleged that a fraudulent check in the amount of {$1200.00} had been deposited into my account through the Wells Fargo mobile banking app. I immediately informed Wells Fargo that I had no knowledge of this transaction, tha
- **cb_opening_onboarding → cb_fraud_disputes** (p 0.98): " A fraudulent bank account and/or loan was opened using my personal information without my consent. I have notified the bank and filed an FTC Identity Theft Report and police report. I did not authorize or benefit from this account or transaction. Please assist in ensuring this fraudulent account i
- **cb_fraud_disputes → ca_card_disputes** (p 0.98): On XX/XX/year>, I was double charged by XXXX XXXX for a bill I was trying to pay online for {$500.00}. I immediately called XXXX XXXX to resolve this and was told I would be issued a refund within 5 days. After not hearing anything back for several days, I filed a claim with Chase Bank on XXXX XXXX.
- **ca_card_applications → cb_fraud_disputes** (p 0.98): I opened a FRAUD/IDENTITY THEFT complaint against CAPITAL ONE XXXX I received a response from them on XXXX. In that response, the details of the fraud are still clear and evident yet, CAPITAL ONE is attempting to use said details as proof to their invalid claims that I have any knowledge of this acc
- **cb_opening_onboarding → cb_account_servicing** (p 0.96): I am filing a formal complaint against JPMorgan Chase regarding a {$3000.00} Chase XXXX XXXX Checking account promotional bonus that has been delayed for nearly three months due to systemic inefficiencies and a complete lack of a clear timeline. Since XX/XX/XXXX, I had already maintained a balance o
- **cb_closures_restrictions → cb_fraud_disputes** (p 0.94): On XX/XX/year>, I received an email from Wells Fargo notifying me that my checking account would be closed because a fraudulent check in the amount of {$15000.00} was deposited into my account on XX/XX/year>. I did not authorize, deposit, or endorse this check, and I immediately disputed the activit
- **cb_fraud_disputes → ca_card_disputes** (p 0.93): On XXXX XXXX XXXX, I made a payment error of {$1000.00} from my U.S. Bank ReliaCard, which contained my unemployment benefit funds. That payment resulted in an unintended overpayment of {$720.00} to my apartment community. After numerous documented attempts to resolve the matter directly with my apa
- **ca_card_personal_loan_servicing → cb_closures_restrictions** (p 0.92): I've filed XXXX complaints with Capital One regarding their fraud department security requirements, as well as the process that this department is required to follow. My initial written complaint was filed on XX/XX/year> against the Fraud Department about the restriction that was placed on my XXXX c
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.9): XXXX XXXX XXXX was closed by the FDIC on XX/XX/XXXX. FDIC became receiver and confirmed my loan was never transferred to JPMorgan Chase. Despite this, Chase recorded a XXXX Assignment of Mortgage to XXXX as Trustee for XXXX XXXX. This assignment is impossible because XXXX no longer existed, the trus
- **cb_opening_onboarding → cb_account_servicing** (p 0.9): BOA offered promotion for XXXX $ bonus for new business checking accounts. I called my local branch and got the code XXXX and entered it, it took. Terms were XXXX $ balance must be funded/maintained by days 30-90. This period has ended last month and I never go the bonus owed. I was given a case fro
- **cb_closures_restrictions → cb_fraud_disputes** (p 0.89): It is well documented. I need the authority that can provide fair relief to take action because the banks actions and inactions have destroyed my life and the bank refuses to provide fair relief. Their previous consent orders and stipulation orders describe what they say they remedied and yet in XXX
- **ca_card_disputes → cb_fraud_disputes** (p 0.88): Capital One Dispute Reconsideration Request Claim # XXXX I am filing a complaint regarding Capital Ones handling of a dispute that was incorrectly classified and ultimately denied. In XXXX, I disputed a charge that was made using my card information without my authorization. This was not a standard 
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.88): Attach this dispute index to every submission Dispute Index / Items Not Mine Furnisher Routing XXXX Account XXXX Open date Dispute reason XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never opened, authorized, signed for, used, or benefited from this account XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never
- **ca_card_applications → cb_fraud_disputes** (p 0.85): I received a credit card from a bank i dont have any attachment, called the institution to check why they sent it, apparently all of my information was in their system requesting a credit also a login for that account was already done i canceled the card and reported it as XXXX, XXXX days after I re
- **ca_card_personal_loan_servicing → sh_credit_bureau_disputes** (p 0.8): I am filing this complaint against Bank of America regarding a credit card account that was recently closed by the creditor without proper justification or notification. Approximately one year ago, the account fell 30 days past due. I immediately brought the account current, resolved the balance, an
- **ca_card_personal_loan_servicing → cb_closures_restrictions** (p 0.74): I have been a U.S. Bank customer for XXXX years ( since XXXX ) and currently maintain another active U.S. Bank credit card. I also recently financed and paid off an auto loan through U.S. Bank. My credit card account, which had been open since XXXX, was recently closed for inactivity. During the per
- **ca_card_personal_loan_servicing → cb_closures_restrictions** (p 0.7): Product : Credit card Company : Citibank , XXXX XXXX Card : XXXX XXXX XXXX XXXX ________________________________________ What happened I did not request closure of my XXXX XXXX XXXX XXXX account. On XX/XX/XXXX, Citibank closed the account, stating the reason was XXXX or more late or returned payment
- **ca_card_personal_loan_servicing → sh_credit_bureau_disputes** (p 0.7): I am filing a complaint regarding a systemic flaw in credit reporting data pipeline mechanics that unfairly penalizes financially responsible consumers. Recently, Citibank/The Home Depot reduced my credit limit solely due to non-use. I do not owe a balance on this account.My complaint is not with th
- **cb_account_servicing → cb_closures_restrictions** (p 0.69): XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX : Attempted to resolve via U.S. Bank Customer Service line ( XXXX ). The automated system completely failed to route me to a live banker or XXXX to address the hardship freeze. XXXX XXXX : Contacted the XXXX XXXX branch directly ( XXXX
- **cb_opening_onboarding → cb_fraud_disputes** (p 0.67): XX/XX/year> @ XXXX- Received an email from Capital One saying my phone number has been updated. XX/XX/year> @ XXXX - Received an email from Capital One saying " Welcome to Credit Wise by Capital One '' XX/XX/year> @ XXXX - Received an email from Capital One saying " Welcome ( my name ), Your new XXX
- **ca_card_applications → cb_fraud_disputes** (p 0.66): A discover credit card was opened by my ex step mother without my consent.
- **cb_fees_overdraft → cb_fraud_disputes** (p 0.65): Ok I bank at Chase Bank. I started with XXXX I had to transfer XXXX into anither savings account. But the XXXX that was left in my savings account has been misused .. every morning when I wake up I start with a transfer, before every transaction I would transfer money, wake up and my account was at 
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.63): My husband has passed away on XX/XX/year>. I contacted Citi to report his death and request that his credit card account be frozen and properly handled. I spoke with XXXX different Citi representatives to speak to the right person repeating the same information. Then, once I could speak to the right
- **ca_card_disputes → cb_fraud_disputes** (p 0.61): XX/XX/XXXX I am contacted by Capital One saying they have identified a potentially fraudulent charge XXXX XXXX XXXX XXXX {$1000.00} I confirm that I did not attempt that transaction I had a car repair that I had planned on charging that day so I called to ask whether I could unlock the card and use 
