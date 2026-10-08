# Triage evaluation — 2026-10-08T23:40:14+00:00

Model: `jev-1.13.0` · Complaints: **2000** (human-labeled: 950) · Reported split: **tune** (development run; test half not revealed)

> Primary answer key on the reported split: 148 human-labeled, 302 labeled by Claude applying the human labeler's rules. Secondary = written rules on consumer-chosen CFPB fields.

## Sub-team
- Accuracy (tune): **81.3%** (95% CI 77.5%–84.7%)
- Calibration error (tune): raw 0.071 → recalibrated 0.044
- Threshold chosen on tune: p ≥ 0.913 (tune coverage 54.7%, lower bound 95.3%)

## Business line
- Accuracy (tune): **88.7%** (95% CI 85.4%–91.3%)
- Calibration error (tune): raw 0.038 → recalibrated 0.046
- Threshold chosen on tune: p ≥ 0.951 (tune coverage 65.3%, lower bound 96.1%)

Secondary key (CFPB rules, 1000 tune complaints): sub-team 53.1%, business line 74.4%
Keyword baseline (tune): accuracy 43.8%
Latency p50/p95: 142 / 182 ms · cost/case $0.000061

## Per sub-team (tune)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| cb_fraud_disputes | Consumer Banking | 116 | 84.8% | 91.4% |
| ca_card_disputes | Card Services & Auto | 68 | 85.5% | 95.6% |
| ca_card_personal_loan_servicing | Card Services & Auto | 60 | 84.8% | 65.0% |
| sh_closures_restrictions | Shared | 60 | 83.6% | 76.7% |
| ca_collections_recoveries | Card Services & Auto | 37 | 93.1% | 73.0% |
| sh_credit_bureau_disputes | Shared | 31 | 82.8% | 77.4% |
| cb_account_servicing (too few to judge) | Consumer Banking | 20 | 54.2% | 65.0% |
| cb_fees_overdraft (too few to judge) | Consumer Banking | 14 | 100.0% | 78.6% |
| ca_card_applications (too few to judge) | Card Services & Auto | 10 | 87.5% | 70.0% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 8 | 33.3% | 75.0% |
| hl_servicing_escrow (too few to judge) | Home Lending | 8 | 100.0% | 75.0% |
| cb_opening_onboarding (too few to judge) | Consumer Banking | 7 | 75.0% | 85.7% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 7 | 60.0% | 85.7% |
| hl_loss_mitigation (too few to judge) | Home Lending | 2 | 66.7% | 100.0% |
| hl_origination (too few to judge) | Home Lending | 2 | 100.0% | 100.0% |

## Tune-half confusions (label → predicted)

- ca_card_personal_loan_servicing → cb_payments_transfers: 6
- cb_fraud_disputes → ca_card_disputes: 5
- sh_closures_restrictions → cb_fraud_disputes: 5
- sh_closures_restrictions → cb_payments_transfers: 4
- sh_credit_bureau_disputes → cb_fraud_disputes: 4
- ca_collections_recoveries → ca_auto_servicing: 4
- cb_fraud_disputes → cb_account_servicing: 4
- ca_card_personal_loan_servicing → cb_account_servicing: 4
- ca_card_personal_loan_servicing → sh_closures_restrictions: 3
- cb_account_servicing → sh_closures_restrictions: 3

## Tune-half error examples (most confident first)

- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I suffered property loss or stolen in the amount of over {$250000.00} when Wells Fargo Bank merge with XXXX XXXX in XXXX. I rented a Safe Deposit Box form XXXX after XXXX XXXX of XXXX and in XXXX with XXXX XXXX XXXX arranged to pay for rental fees with automatic withdrawal over draft protection. XXX
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 1.0): Attach this dispute index to every submission Dispute Index / Items Not Mine Furnisher Routing XXXX Account XXXX Open date Dispute reason XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never opened, authorized, signed for, used, or benefited from this account XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never
- **ca_card_personal_loan_servicing → cb_opening_onboarding** (p 1.0): On Thursday XX/XX/XXXX I contacted Capital One to find out about my dispute for the {$200.00} bonus they will offering when I open my saver account. They did not have my complaint on file and I could not find out why I was denied. The representative said there's XXXX denials XXXX is for the bonus an
- **cb_fraud_disputes → ca_card_disputes** (p 0.99): On XX/XX/year>, I was charged approximately {$1300.00} by XXXX for a reservation. Prior to this charge, I attempted to cancel the reservation before the cancellation policy penalty window was in effect. Despite this, I was still charged the full amount. On XX/XX/year>, I filed a dispute with Wells F
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.99): To Whom It May Concern, I am formally disputing your determination regarding the alleged issuance and negotiation of the check connected to my closed account under case number XXXX. I never received the check that Chase claims was mailed on XX/XX/year>. Additionally, I did not cash, deposit, endorse
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.94): My XXXX credit report shows that I opened an account with Bank of America in XX/XX/year>. I have not opened any credit card with Bank of America at all. I called Bank of America and they said that they do not have a credit card under my Social Security number. XXXX says that the card is mine. The ca
- **sh_closures_restrictions → cb_account_servicing** (p 0.94): I updated my new phone which Citibank two weeks ago I was told it would take 48 hours for my number to be verified in my account two weeks later now its XX/XX/XXXX I call because I dont have access to my account they tell me that the number that I have on file doesnt match its their issue because th
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.93): It is well documented. I need the authority that can provide fair relief to take action because the banks actions and inactions have destroyed my life and the bank refuses to provide fair relief. Their previous consent orders and stipulation orders describe what they say they remedied and yet in XXX
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.92): XXXX XXXX XXXX was closed by the FDIC on XX/XX/XXXX. FDIC became receiver and confirmed my loan was never transferred to JPMorgan Chase. Despite this, Chase recorded a XXXX Assignment of Mortgage to XXXX as Trustee for XXXX XXXX. This assignment is impossible because XXXX no longer existed, the trus
- **sh_closures_restrictions → cb_payments_transfers** (p 0.91): Dear CFPB Complaint Handling Team, I am writing on behalf of XXXX XXXX XXXX XXXX XXXX XXXX, a film production company legally registered in XXXX, to file a formal complaint against JPMorgan Chase Bank regarding the prolonged and unresolved handling of a {$50000.00} check. Case Summary On XX/XX/XXXX,
- **cb_opening_onboarding → ca_card_applications** (p 0.91): Approximately in XXXX 2026 I was denied a joint account with my elderly grandmother with no explanation given from Chase Bank . I have been denied many times before for credit cards as well through this bank with no explanation given. I have never owed them any debt and have had accounts with them i
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.91): Wells Fargo notified me that my deposit accounts had been closed because they alleged that a fraudulent check in the amount of {$1200.00} had been deposited into my account through the Wells Fargo mobile banking app. I immediately informed Wells Fargo that I had no knowledge of this transaction, tha
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.91): Urgent : Fraudulent activity. Freeze account request RE : Formal balance Dispute, Billing errors dispute, Transactions dispute, double billing dispute. XXXX XXXX request. Closed credit card by Wells Fargo in XX/XX/XXXX. This is a formal dispute and emergency request under the FAIR CREDIT BILLING ACT
- **ca_card_personal_loan_servicing → cb_payments_transfers** (p 0.9): In XX/XX/year>, an {$8000.00} balance transfer was sent from XXXX to Chase via a check payable directly to Chase. The check was processed and marked as paid on XX/XX/year>. However, the funds were never applied to the intended account. Because the check was payable to Chase, the funds were received 
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.9): My credit card was charged multiple cash advance fees due to a merchant billing error, not cash advances I initiated. Six fees were charged totaling over {$100.00}. A Wells Fargo representative told me all fees would be refunded after the billing cycle. Two {$10.00} refunds were issued on XX/XX/year
- **ca_collections_recoveries → sh_credit_bureau_disputes** (p 0.88): I recently reviewed my credit report and discovered a collection account listed as XXXX XXXX XXXXXXXX XXXX XXXX XXXXXXXX which I do not recognize and do not believe is accurate. I have not received proper validation of this alleged debt as required under 15 U.S.C. 1692g ( FDCPA ), which mandates tha
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.88): I am writing to dispute and demand reversal of an annual fee charged to my XXXX credit card account immediately prior to the transfer/conversion of the account portfolio to Citibank. XXXX assessed an annual fee to my account on XX/XX/XXXX. I sent a dispute letter to the address located on my stateme
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.88): I contacted Citi to access my credit card statements online as they were unavailable. I reached out numerous times and finally I wrote a better business bureau complaint. The complaint stated that I needed my credit card statement in order to file my taxes. I received a letter and a call from the XX
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.87): I am a XXXX XXXX for XXXX years, enrolled in paperless statements. My billing cycle ends on the XXXX of the month, and I received an email on XX/XX/XXXX notifying my that my paperless statement is available online. The website shows an error message when I attempt to download or view the PDF of my c
- **ca_card_personal_loan_servicing → cb_payments_transfers** (p 0.87): Capital One letter to CFPB XX/XX/year> lied about not being able to find the phone call about not allowing my XXXX payment to go through. I called today and they indeed called me a liar and that I only tried to pay {$2500.00} to XXXX and never tried to pay my monthly premium. I explained thats my AN
- **ca_card_applications → ca_card_disputes** (p 0.85): REGULATORY COMPLAINT : FORMAL REPORT OF SYSTEMIC CREDIT CARD FACTORING, APPLICATION MANIPULATION, AND MULTI-PARTY COLLUSION Target Entities : XXXX XXXX XXXX ( Primary Merchant Account ) XXXX XXXX / XXXX XXXX XXXX XXXX XXXX ) XXXX Summary I am filing this formal complaint with the CFPB to report an o
- **sh_credit_bureau_disputes → ca_card_personal_loan_servicing** (p 0.84): I had a one-time XXXX late payment on my Capital One card due to my grandmother passing .. Ive been a customer for XXXX years with perfect history before/after. I paid the account current and made payment on my other cards to show financial responsibility. I requested a goodwill adjustment to remove
- **ca_collections_recoveries → cb_fraud_disputes** (p 0.83): THIS DEBT WAS FROM IDENTITY THEFT WAY BACK XXXX. I HAVE NO IDEA WHAT PERSON OBTAINED MY IDENTITY OR ACQUIRED A CREDIT CARD INMY NAME. BUT ITS OVER 5 YEARS AND NOW A DEBT BUYER IS RUINING MY CREDIT BASSED UPON AN IDENTITY THEFT ISSUE THAT CITIBANK REFUSED TO FOLLOW THROUGH ON ANY INVESTIGATION. THIS 
- **cb_fraud_disputes → cb_account_servicing** (p 0.82): On XX/XX/2026, I deposited cash into a Chase ATM in multiple batches. The first two deposits were successfully accepted, totaling approximately {$2300.00}, which the bank has acknowledged. During the third deposit, the ATM displayed an updating message, then restarted and showed an error. At one poi
- **cb_account_servicing → cb_fraud_disputes** (p 0.81): So I was online gambling beginning of XXXX and I lost {$17000.00} because Wells Fargo kept on say stating that there were money in my checking account when there was not so every time I requested money to be transferred to an online gambling site it went through thousands of thousands of dollars.
