# Triage evaluation — 2026-10-26T07:54:57+00:00

Model: `jev-1.14.0` · Complaints: **2000** (human-labeled: 950) · Reported split: **test**

> Primary answer key on the reported split: 492 human-labeled, 8 labeled by Claude applying the human labeler's rules. Secondary = written rules on consumer-chosen CFPB fields.

## Sub-team
- Accuracy (test): **77.8%** (95% CI 74.0%–81.2%)
- Calibration error (test): raw 0.095 → recalibrated 0.072
- Threshold chosen on tune: **none** reaches 95.0% on the tune half
- **Test at that threshold:** no threshold to test

## Business line
- Accuracy (test): **83.0%** (95% CI 79.5%–86.0%)
- Calibration error (test): raw 0.088 → recalibrated 0.074
- Threshold chosen on tune: p ≥ 0.885 (tune coverage 69.3%, lower bound 95.0%)
- **Test at that threshold:** coverage 65.6%, precision 93.9%, lower bound 90.8% → **does not pass**

Secondary key (CFPB rules, 1000 test complaints): sub-team 54.7%, business line 74.4%
Keyword baseline (test): accuracy 43.0%
Latency p50/p95: 58 / 109 ms · cost/case $0.000062

## Per sub-team (test)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| cb_fraud_disputes | Consumer Banking | 94 | 73.1% | 92.6% |
| ca_card_disputes | Card Services & Auto | 85 | 88.0% | 77.6% |
| ca_card_personal_loan_servicing | Card Services & Auto | 76 | 85.0% | 67.1% |
| sh_closures_restrictions | Shared | 72 | 73.1% | 79.2% |
| cb_account_servicing | Consumer Banking | 40 | 80.0% | 70.0% |
| ca_collections_recoveries | Card Services & Auto | 33 | 82.9% | 87.9% |
| sh_credit_bureau_disputes (too few to judge) | Shared | 29 | 82.6% | 65.5% |
| cb_opening_onboarding (too few to judge) | Consumer Banking | 16 | 100.0% | 68.8% |
| cb_fees_overdraft (too few to judge) | Consumer Banking | 15 | 86.7% | 86.7% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 15 | 50.0% | 73.3% |
| hl_servicing_escrow (too few to judge) | Home Lending | 10 | 100.0% | 30.0% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 7 | 77.8% | 100.0% |
| ca_card_applications (too few to judge) | Card Services & Auto | 5 | 80.0% | 80.0% |
| hl_loss_mitigation (too few to judge) | Home Lending | 3 | 50.0% | 100.0% |
| hl_origination (too few to judge) | Home Lending | 0 | 0.0% | n/a |

## Tune-half confusions (label → predicted)

- cb_fraud_disputes → ca_card_disputes: 6
- sh_closures_restrictions → cb_fraud_disputes: 4
- ca_collections_recoveries → ca_auto_servicing: 4
- cb_fraud_disputes → cb_account_servicing: 4
- ca_card_personal_loan_servicing → cb_account_servicing: 4
- ca_card_personal_loan_servicing → sh_closures_restrictions: 3
- cb_account_servicing → sh_closures_restrictions: 3
- sh_credit_bureau_disputes → cb_fraud_disputes: 3
- cb_account_servicing → cb_fraud_disputes: 3
- hl_servicing_escrow → hl_loss_mitigation: 3

## Tune-half error examples (most confident first)

- **cb_account_servicing → cb_fraud_disputes** (p 0.99): I suffered property loss or stolen in the amount of over {$250000.00} when Wells Fargo Bank merge with XXXX XXXX in XXXX. I rented a Safe Deposit Box form XXXX after XXXX XXXX of XXXX and in XXXX with XXXX XXXX XXXX arranged to pay for rental fees with automatic withdrawal over draft protection. XXX
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.99): Attach this dispute index to every submission Dispute Index / Items Not Mine Furnisher Routing XXXX Account XXXX Open date Dispute reason XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never opened, authorized, signed for, used, or benefited from this account XXXX XXXX XXXX XXXX XXXX XXXX XX/XX/XXXX Never
- **cb_fraud_disputes → ca_card_disputes** (p 0.98): On XX/XX/year>, I was charged approximately {$1300.00} by XXXX for a reservation. Prior to this charge, I attempted to cancel the reservation before the cancellation policy penalty window was in effect. Despite this, I was still charged the full amount. On XX/XX/year>, I filed a dispute with Wells F
- **ca_card_personal_loan_servicing → cb_opening_onboarding** (p 0.98): On Thursday XX/XX/XXXX I contacted Capital One to find out about my dispute for the {$200.00} bonus they will offering when I open my saver account. They did not have my complaint on file and I could not find out why I was denied. The representative said there's XXXX denials XXXX is for the bonus an
- **sh_closures_restrictions → cb_fraud_disputes** (p 0.97): To Whom It May Concern, I am formally disputing your determination regarding the alleged issuance and negotiation of the check connected to my closed account under case number XXXX. I never received the check that Chase claims was mailed on XX/XX/year>. Additionally, I did not cash, deposit, endorse
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.94): My XXXX credit report shows that I opened an account with Bank of America in XX/XX/year>. I have not opened any credit card with Bank of America at all. I called Bank of America and they said that they do not have a credit card under my Social Security number. XXXX says that the card is mine. The ca
- **sh_credit_bureau_disputes → ca_card_personal_loan_servicing** (p 0.92): I had a one-time XXXX late payment on my Capital One card due to my grandmother passing .. Ive been a customer for XXXX years with perfect history before/after. I paid the account current and made payment on my other cards to show financial responsibility. I requested a goodwill adjustment to remove
- **ca_collections_recoveries → sh_credit_bureau_disputes** (p 0.91): I recently reviewed my credit report and discovered a collection account listed as XXXX XXXX XXXXXXXX XXXX XXXX XXXXXXXX which I do not recognize and do not believe is accurate. I have not received proper validation of this alleged debt as required under 15 U.S.C. 1692g ( FDCPA ), which mandates tha
- **hl_servicing_escrow → hl_loss_mitigation** (p 0.91): XXXX XXXX XXXX was closed by the FDIC on XX/XX/XXXX. FDIC became receiver and confirmed my loan was never transferred to JPMorgan Chase. Despite this, Chase recorded a XXXX Assignment of Mortgage to XXXX as Trustee for XXXX XXXX. This assignment is impossible because XXXX no longer existed, the trus
- **ca_collections_recoveries → ca_card_disputes** (p 0.91): Good Morning, This correspondence serves as a formal follow-up regarding my previously filed complaints with the CFPB under the following case numbers : * XXXX * XXXX * XXXX From the outset of this matter, Wells Fargo has demonstrated a pattern XXXX XXXX, lack of transparency, and procedural failure
- **sh_closures_restrictions → cb_account_servicing** (p 0.89): I updated my new phone which Citibank two weeks ago I was told it would take 48 hours for my number to be verified in my account two weeks later now its XX/XX/XXXX I call because I dont have access to my account they tell me that the number that I have on file doesnt match its their issue because th
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.89): I contacted Citi to access my credit card statements online as they were unavailable. I reached out numerous times and finally I wrote a better business bureau complaint. The complaint stated that I needed my credit card statement in order to file my taxes. I received a letter and a call from the XX
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.87): I called Citibank customer service in XXXX, XXXX and XXXX of XXXX and spoke to a customer service rep each time at length about getting access to historical cc statements online or in the mail for all months XX/XX/XXXX - XX/XX/XXXX. They told me in call # 1 that I would be given access online within
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.86): I am a XXXX XXXX for XXXX years, enrolled in paperless statements. My billing cycle ends on the XXXX of the month, and I received an email on XX/XX/XXXX notifying my that my paperless statement is available online. The website shows an error message when I attempt to download or view the PDF of my c
- **cb_fraud_disputes → cb_account_servicing** (p 0.85): On XX/XX/2026, I deposited cash into a Chase ATM in multiple batches. The first two deposits were successfully accepted, totaling approximately {$2300.00}, which the bank has acknowledged. During the third deposit, the ATM displayed an updating message, then restarted and showed an error. At one poi
- **ca_auto_servicing → ca_card_personal_loan_servicing** (p 0.85): These requests with their canned answers isn't fitting my needs. I am here to complain about Capital One keeping customers at arms length. They only offer a virtual assistant that is not helpful except the most basic needs. I wanted to chat with a human representative but all I get is the run around
- **ca_collections_recoveries → cb_fraud_disputes** (p 0.83): THIS DEBT WAS FROM IDENTITY THEFT WAY BACK XXXX. I HAVE NO IDEA WHAT PERSON OBTAINED MY IDENTITY OR ACQUIRED A CREDIT CARD INMY NAME. BUT ITS OVER 5 YEARS AND NOW A DEBT BUYER IS RUINING MY CREDIT BASSED UPON AN IDENTITY THEFT ISSUE THAT CITIBANK REFUSED TO FOLLOW THROUGH ON ANY INVESTIGATION. THIS 
- **ca_collections_recoveries → ca_auto_servicing** (p 0.83): I entered into a temporary payment reduction ( hardship ) arrangement with Capital One Auto Finance on my auto loan account [ account number ]. The arrangement required a payment of {$370.00} by XX/XX/year>. The bank account previously linked to my Capital One Auto Finance account had been closed du
- **cb_fraud_disputes → cb_account_servicing** (p 0.83): On XX/XX/XXXX at approximately XXXX to XXXX I drove up to a Bank Of America ( Drive Thru ) ATM located at XXXX XXXX, XXXX XXXX, TX XXXX. I inserted my debit card and provided my pin before selecting make deposit. The machine said to insert up to XXXX bills at once. I placed {$3000.00} dollars ( 30x 
- **ca_card_personal_loan_servicing → sh_closures_restrictions** (p 0.82): I am a longtime Capital One credit card customer in good standing. In XX/XX/year>, Capital One revoked my access to XXXX XXXX XXXX numbers without notice or explanation. When I log in, I receive the error : " Looks like you're not eligible. Right now, you are not able to create or use virtual cards 
- **sh_closures_restrictions → cb_payments_transfers** (p 0.8): Dear CFPB Complaint Handling Team, I am writing on behalf of XXXX XXXX XXXX XXXX XXXX XXXX, a film production company legally registered in XXXX, to file a formal complaint against JPMorgan Chase Bank regarding the prolonged and unresolved handling of a {$50000.00} check. Case Summary On XX/XX/XXXX,
- **sh_credit_bureau_disputes → cb_fraud_disputes** (p 0.8): I am disputing a Bank of America account that is the result of identity theft. I submitted a valid identity theft report, including an FTC affidavit and police report, identifying this account as fraudulent. Despite this, Bank of America continues to report the account and has failed to provide any 
- **cb_account_servicing → cb_fraud_disputes** (p 0.8): So I was online gambling beginning of XXXX and I lost {$17000.00} because Wells Fargo kept on say stating that there were money in my checking account when there was not so every time I requested money to be transferred to an online gambling site it went through thousands of thousands of dollars.
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 0.8): I am writing to dispute and demand reversal of an annual fee charged to my XXXX credit card account immediately prior to the transfer/conversion of the account portfolio to Citibank. XXXX assessed an annual fee to my account on XX/XX/XXXX. I sent a dispute letter to the address located on my stateme
- **ca_card_personal_loan_servicing → cb_account_servicing** (p 0.79): I am filing a complaint regarding missing credit card statements after the transfer of my XXXX AAdvantage credit card account to Citi. My XXXX AAdvantage credit card account was transferred to Citi in XX/XX/XXXX. After the transfer, Citi issued me a new card and migrated account access to the Citi w
