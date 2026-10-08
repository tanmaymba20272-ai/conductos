# Triage evaluation — 2026-10-08T23:08:06+00:00

Model: `jev-1.13.0` · Complaints: **2000** (human-labeled: 650) · Reported split: **tune** (development run; test half not revealed)

> Primary answer key = blind human labels (one labeler). Secondary = written rules on consumer-chosen CFPB fields.

## Sub-team
- Accuracy (tune): **86.7%** (95% CI 80.3%–91.2%)
- Calibration error (tune): raw 0.089 → recalibrated 0.070
- Threshold chosen on tune: **none** reaches 95.0% on the tune half

## Business line
- Accuracy (tune): **91.3%** (95% CI 85.7%–94.9%)
- Calibration error (tune): raw 0.058 → recalibrated 0.044
- Threshold chosen on tune: **none** reaches 95.0% on the tune half

Secondary key (CFPB rules, 1000 tune complaints): sub-team 52.7%, business line 74.2%
Keyword baseline (tune): accuracy 49.3%
Latency p50/p95: 87 / 128 ms · cost/case $0.000060

## Per sub-team (tune)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| cb_fraud_disputes | Consumer Banking | 33 | 79.5% | 93.9% |
| ca_card_disputes (too few to judge) | Card Services & Auto | 27 | 93.1% | 100.0% |
| sh_closures_restrictions (too few to judge) | Shared | 21 | 89.5% | 81.0% |
| ca_card_personal_loan_servicing (too few to judge) | Card Services & Auto | 14 | 92.3% | 85.7% |
| ca_collections_recoveries (too few to judge) | Card Services & Auto | 13 | 100.0% | 92.3% |
| cb_account_servicing (too few to judge) | Consumer Banking | 9 | 75.0% | 66.7% |
| sh_credit_bureau_disputes (too few to judge) | Shared | 7 | 100.0% | 71.4% |
| cb_fees_overdraft (too few to judge) | Consumer Banking | 6 | 100.0% | 83.3% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 4 | 60.0% | 75.0% |
| ca_card_applications (too few to judge) | Card Services & Auto | 4 | 100.0% | 75.0% |
| cb_opening_onboarding (too few to judge) | Consumer Banking | 3 | 100.0% | 66.7% |
| hl_servicing_escrow (too few to judge) | Home Lending | 3 | 100.0% | 33.3% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 2 | 66.7% | 100.0% |
| hl_loss_mitigation (too few to judge) | Home Lending | 2 | 50.0% | 100.0% |
| hl_origination (too few to judge) | Home Lending | 2 | 100.0% | 100.0% |

## Tune-half confusions (label → predicted)

- sh_closures_restrictions → cb_fraud_disputes: 3
- cb_fraud_disputes → ca_card_disputes: 2
- hl_servicing_escrow → hl_loss_mitigation: 2
- cb_account_servicing → sh_closures_restrictions: 2
- sh_closures_restrictions → cb_payments_transfers: 1
- cb_payments_transfers → cb_account_servicing: 1
- cb_account_servicing → cb_fraud_disputes: 1
- sh_credit_bureau_disputes → ca_card_personal_loan_servicing: 1
- ca_card_personal_loan_servicing → cb_account_servicing: 1
- ca_card_personal_loan_servicing → cb_payments_transfers: 1

## Tune-half error examples (most confident first)

- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 1.0): Attach this dispute index to every submission Dispute Index / Items Not Mine Furnisher Routing XXXX Account XXXX Open date Dispute reason XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never opened, authorized, signed for, used, or benefited from this account XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never
- **cb_account_servicing → cb_fraud_disputes** (p 0.99): I suffered property loss or stolen in the amount of over {$250000.00} when Wells Fargo Bank merge with XXXX XXXX in XXXX. I rented a Safe Deposit Box form XXXX after XXXX XXXX of XXXX and in XXXX with XXXX XXXX XXXX arranged to pay for rental fees with automatic withdrawal over draft protection. XXX
- **ca_card_applications → cb_fraud_disputes** (p 0.96): I received a credit card from a bank i dont have any attachment, called the institution to check why they sent it, apparently all of my information was in their system requesting a credit also a login for that account was already done i canceled the card and reported it as XXXX, XXXX days after I re
- **cb_opening_onboarding → cb_fraud_disputes** (p 0.94): XX/XX/year> @ XXXX- Received an email from Capital One saying my phone number has been updated. XX/XX/year> @ XXXX - Received an email from Capital One saying " Welcome to Credit Wise by Capital One '' XX/XX/year> @ XXXX - Received an email from Capital One saying " Welcome ( my name ), Your new XXX
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.92): It is well documented. I need the authority that can provide fair relief to take action because the banks actions and inactions have destroyed my life and the bank refuses to provide fair relief. Their previous consent orders and stipulation orders describe what they say they remedied and yet in XXX
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.92): Wells Fargo notified me that my deposit accounts had been closed because they alleged that a fraudulent check in the amount of {$1200.00} had been deposited into my account through the Wells Fargo mobile banking app. I immediately informed Wells Fargo that I had no knowledge of this transaction, tha
- **sh_closures_restrictions → cb_payments_transfers** (p 0.91): Dear CFPB Complaint Handling Team, I am writing on behalf of XXXX XXXX XXXX XXXX XXXX XXXX, a film production company legally registered in XXXX, to file a formal complaint against JPMorgan Chase Bank regarding the prolonged and unresolved handling of a {$50000.00} check. Case Summary On XX/XX/XXXX,
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.9): XXXX XXXX XXXX was closed by the FDIC on XX/XX/XXXX. FDIC became receiver and confirmed my loan was never transferred to JPMorgan Chase. Despite this, Chase recorded a XXXX Assignment of Mortgage to XXXX as Trustee for XXXX XXXX. This assignment is impossible because XXXX no longer existed, the trus
- **sh_credit_bureau_disputes → ca_card_personal_loan_servicing** (p 0.84): I had a one-time XXXX late payment on my Capital One card due to my grandmother passing .. Ive been a customer for XXXX years with perfect history before/after. I paid the account current and made payment on my other cards to show financial responsibility. I requested a goodwill adjustment to remove
- **cb_fraud_disputes → ca_card_disputes** (p 0.75): Fraudulent charges to a vendor which I reported to the bank, they failed to properly investigate. They c closed my claim stating in favor of XXXX due to XXXX providing a XXXX tracking number. What the bank felt to do was to follow up with XXXX and verify the tracking number was me and my address whi
- **cb_fraud_disputes → ca_card_disputes** (p 0.73): On XX/XX/year>, I was double charged by XXXX XXXX for a bill I was trying to pay online for {$500.00}. I immediately called XXXX XXXX to resolve this and was told I would be issued a refund within 5 days. After not hearing anything back for several days, I filed a claim with Chase Bank on XXXX XXXX.
- **cb_account_servicing → sh_closures_restrictions** (p 0.71): Opened an account with Wells Fargo in XXXX. XXXX was told my information was comprimised. Account was never used. Sent me another card and they did an investigation confirming it was hacked. Went down to a branch and closed out account. Next day started getting bombarded with solicitations for credi
- **cb_payments_transfers → cb_account_servicing** (p 0.7): I am submitting this complaint against JPMorgan Chase Bank , N.A . / Chase Bank regarding a foreign currency exchange transaction debited from my Chase checking account ending in XXXX. I initiated the currency exchange transaction on XX/XX/year>, and picked up the XXXX pesos on XX/XX/year>, at the C
- **cb_fees_overdraft → cb_fraud_disputes** (p 0.7): Ok I bank at Chase Bank. I started with XXXX I had to transfer XXXX into anither savings account. But the XXXX that was left in my savings account has been misused .. every morning when I wake up I start with a transfer, before every transaction I would transfer money, wake up and my account was at 
- **ca_collections_recoveries → ca_auto_servicing** (p 0.69): I entered into a temporary payment reduction ( hardship ) arrangement with Capital One Auto Finance on my auto loan account [ account number ]. The arrangement required a payment of {$370.00} by XX/XX/year>. The bank account previously linked to my Capital One Auto Finance account had been closed du
- **cb_account_servicing → sh_closures_restrictions** (p 0.64): XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX : Attempted to resolve via U.S. Bank Customer Service line ( XXXX ). The automated system completely failed to route me to a live banker or XXXX to address the hardship freeze. XXXX XXXX : Contacted the XXXX XXXX branch directly ( XXXX
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.61): I am filing a complaint regarding missing credit card statements after the transfer of my XXXX AAdvantage credit card account to Citi. My XXXX AAdvantage credit card account was transferred to Citi in XX/XX/XXXX. After the transfer, Citi issued me a new card and migrated account access to the Citi w
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.61): On XX/XX/year>, I received an email from Wells Fargo notifying me that my checking account would be closed because a fraudulent check in the amount of {$15000.00} was deposited into my account on XX/XX/year>. I did not authorize, deposit, or endorse this check, and I immediately disputed the activit
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.47): I am filing this formal complaint against JPMorgan Chase Bank , N.A . to demand an immediate executive corporate compliance investigation into unlawful title manufacturing, corporate robosigning, and the clouding of my real property title.JPMorgan Chase Bank, N.A. lacks the legal standing to maintai
- **ca_card_personal_loan_servicing → cb_payments_transfers** (p 0.41): This is a new, escalated complaint regarding deceptive practices and a fraudulent resolution by Capital One under prior XXXX # XXXX. In Capital One 's response to my previous case, they claimed they could not issue my {$170.00} refund check because they needed phone verification. I complied with the
