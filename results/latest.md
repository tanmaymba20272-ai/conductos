# Triage evaluation — 2026-10-08T21:15:32+00:00

Model: `jev-1.13.0` · Complaints: **2000** · Reported split: **tune** (development run; test half not revealed)

> Answer key = written rules on CFPB product, sub-product and issue, which consumers choose when filing; a proxy, not perfect truth.

## Sub-team
- Accuracy (tune): **51.1%** (95% CI 48.0%–54.2%)
- Calibration error (tune): raw 0.354 → recalibrated 0.127
- Threshold chosen on tune: **none** reaches 95.0% on the tune half

## Business line
- Accuracy (tune): **76.4%** (95% CI 73.7%–78.9%)
- Calibration error (tune): raw 0.166 → recalibrated 0.060
- Threshold chosen on tune: **none** reaches 95.0% on the tune half

Keyword baseline (tune): accuracy 40.6%
Latency p50/p95: 147 / 191 ms · cost/case $0.000056

## Per sub-team (tune)

| sub-team | line | support | precision | recall |
|---|---|---|---|---|
| ca_card_personal_loan_servicing | Card Services & Auto | 210 | 85.6% | 51.0% |
| cb_account_servicing | Consumer Banking | 207 | 69.5% | 19.8% |
| ca_card_disputes | Card Services & Auto | 162 | 63.6% | 76.5% |
| cb_fraud_disputes | Consumer Banking | 94 | 26.0% | 68.1% |
| ca_collections_recoveries | Card Services & Auto | 89 | 75.9% | 49.4% |
| cb_closures_restrictions | Consumer Banking | 49 | 31.5% | 71.4% |
| cb_opening_onboarding | Consumer Banking | 37 | 92.9% | 35.1% |
| cb_fees_overdraft | Consumer Banking | 36 | 72.4% | 58.3% |
| ca_card_applications (too few to judge) | Card Services & Auto | 28 | 31.2% | 17.9% |
| sh_credit_bureau_disputes (too few to judge) | Shared | 21 | 18.7% | 66.7% |
| cb_payments_transfers (too few to judge) | Consumer Banking | 18 | 36.7% | 61.1% |
| ca_auto_servicing (too few to judge) | Card Services & Auto | 18 | 61.1% | 61.1% |
| hl_servicing_escrow (too few to judge) | Home Lending | 16 | 90.9% | 62.5% |
| hl_loss_mitigation (too few to judge) | Home Lending | 11 | 90.0% | 81.8% |
| hl_origination (too few to judge) | Home Lending | 4 | 66.7% | 50.0% |

## Tune-half confusions (label → predicted)

- cb_account_servicing → cb_fraud_disputes: 85
- cb_account_servicing → cb_closures_restrictions: 38
- ca_collections_recoveries → sh_credit_bureau_disputes: 29
- cb_account_servicing → ca_card_disputes: 27
- ca_card_disputes → cb_fraud_disputes: 25
- ca_card_personal_loan_servicing → ca_card_disputes: 21
- ca_card_personal_loan_servicing → cb_closures_restrictions: 20
- ca_card_personal_loan_servicing → cb_fraud_disputes: 19
- cb_fraud_disputes → ca_card_disputes: 19
- ca_card_applications → cb_fraud_disputes: 16

## Tune-half error examples (most confident first)

- **cb_account_servicing → cb_fraud_disputes** (p 1.0): On XX/XX/year>, at approximately XXXX XXXX, I became the victim of a coercionbased fraud scheme. I received a phone call from an individual falsely claiming to be affiliated with the XXXX XXXX Police Department. The caller ID displayed a local government number, which I later learned was spoofed. I 
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): On XX/XX/year>, my wallet containing my drivers license, credit cards, and phone was stolen. I filed a police report the same day. I immediately contacted Chase Bank to report the theft and any unauthorized activity. Starting Monday, XX/XX/year>, and on subsequent days, I visited my local Chase bran
- **cb_fraud_disputes → ca_card_disputes** (p 1.0): On XX/XX/year>, I was charged approximately {$1300.00} by XXXX for a reservation. Prior to this charge, I attempted to cancel the reservation before the cancellation policy penalty window was in effect. Despite this, I was still charged the full amount. On XX/XX/year>, I filed a dispute with Wells F
- **cb_fees_overdraft → cb_fraud_disputes** (p 1.0): I am a victim of identity theft. My checking account with Wells Fargo ending in XXXX was compromised and unauthorized deposits and transactions totaling approximately {$31000.00} were made without my knowledge or consent. This activity does not reflect my normal banking behavior. I did not authorize
- **cb_account_servicing → ca_card_disputes** (p 1.0): Wells Fargo denied my debit card dispute ( # XXXX ) despite photographic proof of merchant overcharging. On XX/XX/year> ( Thursday, XXXX ), XXXX XXXX XXXX XXXX charged my debit card {$99.00} total ( {$31.00} + {$68.00} ). Their own menu states " Weekend Dinner Only Price '' ( {$24.00}.
- **cb_fees_overdraft → cb_account_servicing** (p 1.0): Hi please help me I need to pay my car loan and my car insurance today Today XX/XX/year> XXXXXXXX XXXX XXXXXXXX going to Chase Bank XXXX XXXX XXXX XXXX NY XXXX XXXX take from home XXXXXXXX XXXX XXXXash to deposit to my checking account # XXXX XXXX go inside to the bank and use 1 of 3 ATM machine to 
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I had a Bank America account under EDD debit card, somebody hacked My account Withdraw with XXXX XXXX {$15000.00} in less than XXXX days from XX/XX/year> till XX/XX/year> total of XXXX, But Bank of America have not solved this problem claim # XXXX, # XXXX And they denied my claim over and over, I fo
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I am filing a complaint regarding an unauthorized transfer from my Bank of America account that was denied as a valid transaction. An unknown individual impersonated me over the phone, gained access to my account, transferred {$4900.00} internally, and then sent {$3500.00} externally through a third
- **ca_collections_recoveries → sh_credit_bureau_disputes** (p 1.0): I am filing this complaint to dispute inaccurate and unverified information being reported on my credit file. The account listed as Wells Fargo, account number XXXX, is currently being reported on my credit report. I formally dispute the accuracy and completeness of this account. Under the Fair Cred
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I am a second generation Citibank account holder, having held my account ( XXXX ) with them for over a decade. Late XXXX, my account XXXX was hacked and subsequently drained. In XX/XX/XXXX, both my savings ( ending in XXXX ) and checking ( ending in XXXX ) accounts were compromised. An individual ot
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): On XX/XX/year> at XXXX XXXX, I discovered I had been the victim of bank fraud involving my Capital One savings account. I opened my account online today to retrieve checking information for tax filing purposes. Upon reviewing my savings balance, I noticed my funds were considerably lower than expect
- **cb_account_servicing → ca_card_disputes** (p 1.0): I placed an order through XXXX for sushi that arrived completely rotten and inedible. I immediately contacted XXXX for resolution and was denied any remedy. I then filed a dispute with Capital One to recover funds for goods that were never delivered in acceptable condition. Throughout the dispute pr
- **cb_account_servicing → cb_fees_overdraft** (p 1.0): On dates : XX/XX/scrub>XXXX XXXX XXXX XXXX XXXXXX/XX/year>, I was charged multiple overdraft fees on my Wells Fargo checking account totaling {$210.00}. This included XXXX separate {$35.00} overdraft fees assessed on the same day. At the time these transactions were processed, my account did not app
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): Subject : Complaint Regarding Mishandling of Fraud Victim Case and Account Restriction I am submitting this complaint regarding my experience with JPMorgan Chase Bank, N.A. concerning a fraud incident that has resulted in account restrictions and a negative balance for which I am being held responsi
- **cb_account_servicing → cb_closures_restrictions** (p 1.0): My bank accounts was closed without notification checking and saving and the bank refused to let me know why after I've been with them for almost XXXX years
- **ca_card_applications → cb_fraud_disputes** (p 1.0): Wells Fargo Fraud Department called me that some one used Wells Fargo bank credit card with my name in XXXX purchasing XXXX XXXX. That card was issued in XXXX this year at the XXXX Wells Fargo branch. I never applied this card, have not been in XXXX for a long time. They connect me to FTC so I repor
- **ca_card_personal_loan_servicing → ca_card_disputes** (p 1.0): Subject : Formal Complaint Failure to Properly Investigate Dispute ( Billing Error / Service Not Rendered / Misrepresentation ) To Whom It May Concern, I am filing a formal complaint regarding the handling of my credit card dispute by Capital One. Despite submitting a legitimate dispute concerning a
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): Dear Consumer Financial Protection Bureau, I am writing to formally file a complaint regarding unauthorized transactions on my account and the subsequent denial of my dispute by Citibank. On XX/XX/year>, my account ending in XXXX was compromised for a total amount of {$1800.00}. I was contacted by X
- **ca_collections_recoveries → sh_credit_bureau_disputes** (p 1.0): Additional XXXX XXXX of XXXX I am supplementing my complaint XXXX reflect the sequence of events following submission. On XX/XX/XXXX, I submitted this complaint XXXX the CFPB disputing the accuracy and internal consistency of the Bank of America tradeline and requesting a full investigation and reco
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I have a bussines account with chase bank, over a period of time, someone to who I wrote checks, saved the physical hard copy of the checks and deposited as much of 3 times the same check, over a period of 18 months, even the checks were dated from XXXX and XXXX, I noticed once back in XXXX of XXXX,
- **ca_card_disputes → sh_credit_bureau_disputes** (p 1.0): I was in the process of applying for a VA loan. I had a single 30 day late payment on my account that I didnt dispute, but asked if I could have a goodwill deletion of the status. Although she said she would remove it, I received a mailed response to the contrary and they have marked my credit file 
- **ca_card_disputes → cb_fraud_disputes** (p 1.0): I received a call from XXXX. The agent advised her name was XXXX from Bank of America and she was checking on suspicious charges on my credit card. I have never done business with this bank and do not have a card with them. She said the card was under my name and had been used in New York to purchas
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): I am filing this complaint regarding a fraud loss of approximately {$16000.00} from my account due to a coordinated impersonation scam involving individuals posing as Wells Fargos fraud department. On XX/XX/year>, I received a text message that appeared to be from Wells Fargo fraud services stating 
- **cb_account_servicing → cb_fraud_disputes** (p 1.0): Hello, recently someone stole my social security information and they made a very big withdrawal from my account of {$6000.00} ). The bank ( Chase ) refusing to give me my money back even after i opened a claim with them. I honestly dont know what to do as Im loosing my mind over this. Chase suppose
- **ca_card_personal_loan_servicing → sh_credit_bureau_disputes** (p 1.0): I am filing a formal complaint regarding inaccurate credit reporting by Capital One. I have maintained a consistent and reliable payment history on this account since it was opened on XX/XX/year>. However, Capital One is reporting a XXXX late payment for XX/XX/year>, which is not an accurate reflect
