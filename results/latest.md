# Triage evaluation — 2026-10-09T00:08:49+00:00

Model: `jev-1.13.0` · Complaints: **2000** (human-labeled: 950) · Reported split: **test**

> Primary answer key on the reported split: 492 human-labeled, 8 labeled by Claude applying the human labeler's rules. Secondary = written rules on consumer-chosen CFPB fields.

## Sub-team
- Accuracy (test): **76.2%** (95% CI 72.3%–79.7%)
- Calibration error (test): raw 0.115 → recalibrated 0.080
- Threshold chosen on tune: p ≥ 0.936 (tune coverage 57.6%, lower bound 95.0%)
- **Test at that threshold:** coverage 56.4%, precision 90.1%, lower bound 86.0% → **does not pass**

## Business line
- Accuracy (test): **82.6%** (95% CI 79.0%–85.7%)
- Calibration error (test): raw 0.093 → recalibrated 0.074
- Threshold chosen on tune: p ≥ 0.884 (tune coverage 69.6%, lower bound 95.5%)
- **Test at that threshold:** coverage 68.2%, precision 91.8%, lower bound 88.4% → **does not pass**

Secondary key (CFPB rules, 1000 test complaints): sub-team 53.8%, business line 74.4%
Keyword baseline (test): accuracy 43.0%
Latency p50/p95: 120 / 159 ms · cost/case $0.000062

## Per sub-team (test)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| cb_fraud_disputes | Consumer Banking | 94 | 70.5% | 91.5% |
| ca_card_disputes | Card Services & Auto | 85 | 86.8% | 77.6% |
| ca_card_personal_loan_servicing | Card Services & Auto | 76 | 85.7% | 71.1% |
| sh_closures_restrictions | Shared | 72 | 73.6% | 73.6% |
| cb_account_servicing | Consumer Banking | 40 | 73.5% | 62.5% |
| ca_collections_recoveries | Card Services & Auto | 33 | 81.8% | 81.8% |
| sh_credit_bureau_disputes (too few to judge) | Shared | 29 | 76.9% | 69.0% |
| cb_opening_onboarding (too few to judge) | Consumer Banking | 16 | 100.0% | 68.8% |
| cb_fees_overdraft (too few to judge) | Consumer Banking | 15 | 86.7% | 86.7% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 15 | 45.0% | 60.0% |
| hl_servicing_escrow (too few to judge) | Home Lending | 10 | 100.0% | 30.0% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 7 | 77.8% | 100.0% |
| ca_card_applications (too few to judge) | Card Services & Auto | 5 | 66.7% | 80.0% |
| hl_loss_mitigation (too few to judge) | Home Lending | 3 | 50.0% | 100.0% |
| hl_origination (too few to judge) | Home Lending | 0 | 0.0% | n/a |

## Tune-half confusions (label → predicted)

- cb_fraud_disputes → ca_card_disputes: 6
- sh_closures_restrictions → cb_fraud_disputes: 5
- sh_credit_bureau_disputes → cb_fraud_disputes: 5
- sh_closures_restrictions → cb_payments_transfers: 4
- ca_collections_recoveries → ca_auto_servicing: 4
- cb_fraud_disputes → cb_account_servicing: 4
- ca_card_personal_loan_servicing → cb_account_servicing: 4
- cb_account_servicing → sh_closures_restrictions: 3
- ca_collections_recoveries → sh_credit_bureau_disputes: 3
- sh_closures_restrictions → ca_card_personal_loan_servicing: 3

## Tune-half error examples (most confident first)

- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I suffered property loss or stolen in the amount of over {$250000.00} when Wells Fargo Bank merge with XXXX XXXX in XXXX. I rented a Safe Deposit Box form XXXX after XXXX XXXX of XXXX and in XXXX with XXXX XXXX XXXX arranged to pay for rental fees with automatic withdrawal over draft protection. XXX
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 1.0): Attach this dispute index to every submission Dispute Index / Items Not Mine Furnisher Routing XXXX Account XXXX Open date Dispute reason XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never opened, authorized, signed for, used, or benefited from this account XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never
- **ca_card_personal_loan_servicing → cb_opening_onboarding** (p 1.0): On Thursday XX/XX/XXXX I contacted Capital One to find out about my dispute for the {$200.00} bonus they will offering when I open my saver account. They did not have my complaint on file and I could not find out why I was denied. The representative said there's XXXX denials XXXX is for the bonus an
- **cb_fraud_disputes → ca_card_disputes** (p 0.99): On XX/XX/year>, I was charged approximately {$1300.00} by XXXX for a reservation. Prior to this charge, I attempted to cancel the reservation before the cancellation policy penalty window was in effect. Despite this, I was still charged the full amount. On XX/XX/year>, I filed a dispute with Wells F
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.99): To Whom It May Concern, I am formally disputing your determination regarding the alleged issuance and negotiation of the check connected to my closed account under case number XXXX. I never received the check that Chase claims was mailed on XX/XX/year>. Additionally, I did not cash, deposit, endorse
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.95): It is well documented. I need the authority that can provide fair relief to take action because the banks actions and inactions have destroyed my life and the bank refuses to provide fair relief. Their previous consent orders and stipulation orders describe what they say they remedied and yet in XXX
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.94): My XXXX credit report shows that I opened an account with Bank of America in XX/XX/year>. I have not opened any credit card with Bank of America at all. I called Bank of America and they said that they do not have a credit card under my Social Security number. XXXX says that the card is mine. The ca
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.92): Wells Fargo notified me that my deposit accounts had been closed because they alleged that a fraudulent check in the amount of {$1200.00} had been deposited into my account through the Wells Fargo mobile banking app. I immediately informed Wells Fargo that I had no knowledge of this transaction, tha
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.91): XXXX XXXX XXXX was closed by the FDIC on XX/XX/XXXX. FDIC became receiver and confirmed my loan was never transferred to JPMorgan Chase. Despite this, Chase recorded a XXXX Assignment of Mortgage to XXXX as Trustee for XXXX XXXX. This assignment is impossible because XXXX no longer existed, the trus
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.9): I am a XXXX XXXX for XXXX years, enrolled in paperless statements. My billing cycle ends on the XXXX of the month, and I received an email on XX/XX/XXXX notifying my that my paperless statement is available online. The website shows an error message when I attempt to download or view the PDF of my c
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.9): I contacted Citi to access my credit card statements online as they were unavailable. I reached out numerous times and finally I wrote a better business bureau complaint. The complaint stated that I needed my credit card statement in order to file my taxes. I received a letter and a call from the XX
- **sh_closures_restrictions → cb_account_servicing** (p 0.89): I updated my new phone which Citibank two weeks ago I was told it would take 48 hours for my number to be verified in my account two weeks later now its XX/XX/XXXX I call because I dont have access to my account they tell me that the number that I have on file doesnt match its their issue because th
- **ca_card_applications → ca_card_disputes** (p 0.89): REGULATORY COMPLAINT : FORMAL REPORT OF SYSTEMIC CREDIT CARD FACTORING, APPLICATION MANIPULATION, AND MULTI-PARTY COLLUSION Target Entities : XXXX XXXX XXXX ( Primary Merchant Account ) XXXX XXXX / XXXX XXXX XXXX XXXX XXXX ) XXXX Summary I am filing this formal complaint with the CFPB to report an o
- **ca_collections_recoveries → sh_credit_bureau_disputes** (p 0.87): I recently reviewed my credit report and discovered a collection account listed as XXXX XXXX XXXXXXXX XXXX XXXX XXXXXXXX which I do not recognize and do not believe is accurate. I have not received proper validation of this alleged debt as required under 15 U.S.C. 1692g ( FDCPA ), which mandates tha
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.87): I am writing to dispute and demand reversal of an annual fee charged to my XXXX credit card account immediately prior to the transfer/conversion of the account portfolio to Citibank. XXXX assessed an annual fee to my account on XX/XX/XXXX. I sent a dispute letter to the address located on my stateme
- **ca_auto_servicing → ca_card_personal_loan_servicing** (p 0.87): These requests with their canned answers isn't fitting my needs. I am here to complain about Capital One keeping customers at arms length. They only offer a virtual assistant that is not helpful except the most basic needs. I wanted to chat with a human representative but all I get is the run around
- **sh_closures_restrictions → ca_card_personal_loan_servicing** (p 0.85): XXXX initiated a new verification process for my credit card. The link didnt work so I called in. A new card was opened, but was not linked to my XXXX app or current credit card. I continued to pay the balance of my credit card through the app every month but the new card was not linked nor paid whi
- **cb_opening_onboarding → ca_card_applications** (p 0.85): Approximately in XXXX 2026 I was denied a joint account with my elderly grandmother with no explanation given from Chase Bank . I have been denied many times before for credit cards as well through this bank with no explanation given. I have never owed them any debt and have had accounts with them i
- **ca_collections_recoveries → cb_fraud_disputes** (p 0.83): THIS DEBT WAS FROM IDENTITY THEFT WAY BACK XXXX. I HAVE NO IDEA WHAT PERSON OBTAINED MY IDENTITY OR ACQUIRED A CREDIT CARD INMY NAME. BUT ITS OVER 5 YEARS AND NOW A DEBT BUYER IS RUINING MY CREDIT BASSED UPON AN IDENTITY THEFT ISSUE THAT CITIBANK REFUSED TO FOLLOW THROUGH ON ANY INVESTIGATION. THIS 
- **cb_account_servicing → cb_fraud_disputes** (p 0.82): So I was online gambling beginning of XXXX and I lost {$17000.00} because Wells Fargo kept on say stating that there were money in my checking account when there was not so every time I requested money to be transferred to an online gambling site it went through thousands of thousands of dollars.
- **ca_card_personal_loan_servicing → sh_closures_restrictions** (p 0.81): I am a longtime Capital One credit card customer in good standing. In XX/XX/year>, Capital One revoked my access to XXXX XXXX XXXX numbers without notice or explanation. When I log in, I receive the error : " Looks like you're not eligible. Right now, you are not able to create or use virtual cards 
- **cb_fraud_disputes → cb_account_servicing** (p 0.81): On XX/XX/2026, I deposited cash into a Chase ATM in multiple batches. The first two deposits were successfully accepted, totaling approximately {$2300.00}, which the bank has acknowledged. During the third deposit, the ATM displayed an updating message, then restarted and showed an error. At one poi
- **sh_credit_bureau_disputes → ca_card_personal_loan_servicing** (p 0.81): I had a one-time XXXX late payment on my Capital One card due to my grandmother passing .. Ive been a customer for XXXX years with perfect history before/after. I paid the account current and made payment on my other cards to show financial responsibility. I requested a goodwill adjustment to remove
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.81): I called Citibank customer service in XXXX, XXXX and XXXX of XXXX and spoke to a customer service rep each time at length about getting access to historical cc statements online or in the mail for all months XX/XX/XXXX - XX/XX/XXXX. They told me in call # 1 that I would be given access online within
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.81): Urgent : Fraudulent activity. Freeze account request RE : Formal balance Dispute, Billing errors dispute, Transactions dispute, double billing dispute. XXXX XXXX request. Closed credit card by Wells Fargo in XX/XX/XXXX. This is a formal dispute and emergency request under the FAIR CREDIT BILLING ACT
