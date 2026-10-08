# Triage evaluation — 2026-10-08T23:57:12+00:00

Model: `jev-1.13.0` · Complaints: **2000** (human-labeled: 950) · Reported split: **tune** (development run; test half not revealed)

> Primary answer key on the reported split: 148 human-labeled, 302 labeled by Claude applying the human labeler's rules. Secondary = written rules on consumer-chosen CFPB fields.

## Sub-team
- Accuracy (tune): **83.6%** (95% CI 79.8%–86.7%)
- Calibration error (tune): raw 0.064 → recalibrated 0.031
- Threshold chosen on tune: p ≥ 0.903 (tune coverage 57.6%, lower bound 95.6%)

## Business line
- Accuracy (tune): **89.8%** (95% CI 86.6%–92.2%)
- Calibration error (tune): raw 0.042 → recalibrated 0.031
- Threshold chosen on tune: p ≥ 0.935 (tune coverage 66.9%, lower bound 95.3%)

Secondary key (CFPB rules, 1000 tune complaints): sub-team 53.8%, business line 74.8%
Keyword baseline (tune): accuracy 43.8%
Latency p50/p95: 140 / 182 ms · cost/case $0.000062

## Per sub-team (tune)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| cb_fraud_disputes | Consumer Banking | 116 | 85.6% | 92.2% |
| ca_card_disputes | Card Services & Auto | 68 | 88.0% | 97.1% |
| ca_card_personal_loan_servicing | Card Services & Auto | 60 | 88.0% | 73.3% |
| sh_closures_restrictions | Shared | 60 | 85.5% | 78.3% |
| ca_collections_recoveries | Card Services & Auto | 37 | 96.4% | 73.0% |
| sh_credit_bureau_disputes | Shared | 31 | 89.3% | 80.6% |
| cb_account_servicing (too few to judge) | Consumer Banking | 20 | 54.2% | 65.0% |
| cb_fees_overdraft (too few to judge) | Consumer Banking | 14 | 100.0% | 78.6% |
| ca_card_applications (too few to judge) | Card Services & Auto | 10 | 88.9% | 80.0% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 8 | 40.0% | 75.0% |
| hl_servicing_escrow (too few to judge) | Home Lending | 8 | 100.0% | 75.0% |
| cb_opening_onboarding (too few to judge) | Consumer Banking | 7 | 75.0% | 85.7% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 7 | 60.0% | 85.7% |
| hl_loss_mitigation (too few to judge) | Home Lending | 2 | 50.0% | 100.0% |
| hl_origination (too few to judge) | Home Lending | 2 | 100.0% | 100.0% |

## Tune-half confusions (label → predicted)

- sh_closures_restrictions → cb_fraud_disputes: 5
- cb_fraud_disputes → ca_card_disputes: 4
- sh_closures_restrictions → cb_payments_transfers: 4
- sh_credit_bureau_disputes → cb_fraud_disputes: 4
- ca_collections_recoveries → ca_auto_servicing: 4
- cb_fraud_disputes → cb_account_servicing: 4
- ca_card_personal_loan_servicing → cb_account_servicing: 4
- cb_account_servicing → sh_closures_restrictions: 3
- ca_collections_recoveries → sh_credit_bureau_disputes: 3
- sh_closures_restrictions → ca_card_personal_loan_servicing: 3

## Tune-half error examples (most confident first)

- **cb_fraud_disputes → ca_card_disputes** (p 1.0): On XX/XX/year>, I was charged approximately {$1300.00} by XXXX for a reservation. Prior to this charge, I attempted to cancel the reservation before the cancellation policy penalty window was in effect. Despite this, I was still charged the full amount. On XX/XX/year>, I filed a dispute with Wells F
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I suffered property loss or stolen in the amount of over {$250000.00} when Wells Fargo Bank merge with XXXX XXXX in XXXX. I rented a Safe Deposit Box form XXXX after XXXX XXXX of XXXX and in XXXX with XXXX XXXX XXXX arranged to pay for rental fees with automatic withdrawal over draft protection. XXX
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 1.0): Attach this dispute index to every submission Dispute Index / Items Not Mine Furnisher Routing XXXX Account XXXX Open date Dispute reason XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never opened, authorized, signed for, used, or benefited from this account XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never
- **ca_card_personal_loan_servicing → cb_opening_onboarding** (p 1.0): On Thursday XX/XX/XXXX I contacted Capital One to find out about my dispute for the {$200.00} bonus they will offering when I open my saver account. They did not have my complaint on file and I could not find out why I was denied. The representative said there's XXXX denials XXXX is for the bonus an
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.99): To Whom It May Concern, I am formally disputing your determination regarding the alleged issuance and negotiation of the check connected to my closed account under case number XXXX. I never received the check that Chase claims was mailed on XX/XX/year>. Additionally, I did not cash, deposit, endorse
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.93): My XXXX credit report shows that I opened an account with Bank of America in XX/XX/year>. I have not opened any credit card with Bank of America at all. I called Bank of America and they said that they do not have a credit card under my Social Security number. XXXX says that the card is mine. The ca
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.93): It is well documented. I need the authority that can provide fair relief to take action because the banks actions and inactions have destroyed my life and the bank refuses to provide fair relief. Their previous consent orders and stipulation orders describe what they say they remedied and yet in XXX
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.93): I am a XXXX XXXX for XXXX years, enrolled in paperless statements. My billing cycle ends on the XXXX of the month, and I received an email on XX/XX/XXXX notifying my that my paperless statement is available online. The website shows an error message when I attempt to download or view the PDF of my c
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.93): Wells Fargo notified me that my deposit accounts had been closed because they alleged that a fraudulent check in the amount of {$1200.00} had been deposited into my account through the Wells Fargo mobile banking app. I immediately informed Wells Fargo that I had no knowledge of this transaction, tha
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.92): XXXX XXXX XXXX was closed by the FDIC on XX/XX/XXXX. FDIC became receiver and confirmed my loan was never transferred to JPMorgan Chase. Despite this, Chase recorded a XXXX Assignment of Mortgage to XXXX as Trustee for XXXX XXXX. This assignment is impossible because XXXX no longer existed, the trus
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.9): I contacted Citi to access my credit card statements online as they were unavailable. I reached out numerous times and finally I wrote a better business bureau complaint. The complaint stated that I needed my credit card statement in order to file my taxes. I received a letter and a call from the XX
- **ca_card_applications → ca_card_disputes** (p 0.9): REGULATORY COMPLAINT : FORMAL REPORT OF SYSTEMIC CREDIT CARD FACTORING, APPLICATION MANIPULATION, AND MULTI-PARTY COLLUSION Target Entities : XXXX XXXX XXXX ( Primary Merchant Account ) XXXX XXXX / XXXX XXXX XXXX XXXX XXXX ) XXXX Summary I am filing this formal complaint with the CFPB to report an o
- **ca_collections_recoveries → sh_credit_bureau_disputes** (p 0.88): I recently reviewed my credit report and discovered a collection account listed as XXXX XXXX XXXXXXXX XXXX XXXX XXXXXXXX which I do not recognize and do not believe is accurate. I have not received proper validation of this alleged debt as required under 15 U.S.C. 1692g ( FDCPA ), which mandates tha
- **sh_closures_restrictions → cb_account_servicing** (p 0.88): I updated my new phone which Citibank two weeks ago I was told it would take 48 hours for my number to be verified in my account two weeks later now its XX/XX/XXXX I call because I dont have access to my account they tell me that the number that I have on file doesnt match its their issue because th
- **ca_auto_servicing → ca_card_personal_loan_servicing** (p 0.87): These requests with their canned answers isn't fitting my needs. I am here to complain about Capital One keeping customers at arms length. They only offer a virtual assistant that is not helpful except the most basic needs. I wanted to chat with a human representative but all I get is the run around
- **sh_closures_restrictions → cb_payments_transfers** (p 0.86): Dear CFPB Complaint Handling Team, I am writing on behalf of XXXX XXXX XXXX XXXX XXXX XXXX, a film production company legally registered in XXXX, to file a formal complaint against JPMorgan Chase Bank regarding the prolonged and unresolved handling of a {$50000.00} check. Case Summary On XX/XX/XXXX,
- **cb_opening_onboarding → ca_card_applications** (p 0.86): Approximately in XXXX 2026 I was denied a joint account with my elderly grandmother with no explanation given from Chase Bank . I have been denied many times before for credit cards as well through this bank with no explanation given. I have never owed them any debt and have had accounts with them i
- **sh_credit_bureau_disputes → ca_card_personal_loan_servicing** (p 0.85): I had a one-time XXXX late payment on my Capital One card due to my grandmother passing .. Ive been a customer for XXXX years with perfect history before/after. I paid the account current and made payment on my other cards to show financial responsibility. I requested a goodwill adjustment to remove
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.84): I am writing to dispute and demand reversal of an annual fee charged to my XXXX credit card account immediately prior to the transfer/conversion of the account portfolio to Citibank. XXXX assessed an annual fee to my account on XX/XX/XXXX. I sent a dispute letter to the address located on my stateme
- **sh_closures_restrictions → ca_card_personal_loan_servicing** (p 0.84): XXXX initiated a new verification process for my credit card. The link didnt work so I called in. A new card was opened, but was not linked to my XXXX app or current credit card. I continued to pay the balance of my credit card through the app every month but the new card was not linked nor paid whi
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.84): I called Citibank customer service in XXXX, XXXX and XXXX of XXXX and spoke to a customer service rep each time at length about getting access to historical cc statements online or in the mail for all months XX/XX/XXXX - XX/XX/XXXX. They told me in call # 1 that I would be given access online within
- **cb_account_servicing → cb_fraud_disputes** (p 0.82): So I was online gambling beginning of XXXX and I lost {$17000.00} because Wells Fargo kept on say stating that there were money in my checking account when there was not so every time I requested money to be transferred to an online gambling site it went through thousands of thousands of dollars.
- **ca_card_personal_loan_servicing → sh_closures_restrictions** (p 0.82): I am a longtime Capital One credit card customer in good standing. In XX/XX/year>, Capital One revoked my access to XXXX XXXX XXXX numbers without notice or explanation. When I log in, I receive the error : " Looks like you're not eligible. Right now, you are not able to create or use virtual cards 
- **cb_account_servicing → cb_payments_transfers** (p 0.82): I initiated a {$1000.00} ach transfer with Citibank on Friday morning XX/XX/year> at approximately XXXX to my Citi account from my bank account with XXXX XXXX XXXX XXXX Citi received and posted the funds that Friday afternoon, but balance is not reflected in my available balance. I called customer s
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.81): Urgent : Fraudulent activity. Freeze account request RE : Formal balance Dispute, Billing errors dispute, Transactions dispute, double billing dispute. XXXX XXXX request. Closed credit card by Wells Fargo in XX/XX/XXXX. This is a formal dispute and emergency request under the FAIR CREDIT BILLING ACT
