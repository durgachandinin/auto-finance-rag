"""
generate_sample_data.py
Creates sample automotive finance documents for testing the RAG pipeline.
Run this once to populate data/ with realistic test content.
"""

import os
import csv

# ── Sample CSV: vehicle financing rates ──────────────────────────────────────
rates_data = [
    ["Vehicle Type", "Credit Score Range", "Loan Term (months)", "APR (%)", "Max LTV (%)"],
    ["New Car", "750-850", "36", "4.99", "110"],
    ["New Car", "750-850", "48", "5.49", "110"],
    ["New Car", "750-850", "60", "5.99", "110"],
    ["New Car", "750-850", "72", "6.49", "100"],
    ["New Car", "700-749", "36", "6.49", "105"],
    ["New Car", "700-749", "48", "6.99", "105"],
    ["New Car", "700-749", "60", "7.49", "105"],
    ["New Car", "700-749", "72", "7.99", "100"],
    ["New Car", "650-699", "36", "9.99", "100"],
    ["New Car", "650-699", "48", "10.49", "100"],
    ["New Car", "650-699", "60", "10.99", "100"],
    ["Used Car (0-2 yrs)", "750-850", "36", "5.99", "100"],
    ["Used Car (0-2 yrs)", "750-850", "48", "6.49", "100"],
    ["Used Car (0-2 yrs)", "750-850", "60", "6.99", "100"],
    ["Used Car (0-2 yrs)", "700-749", "36", "7.99", "95"],
    ["Used Car (0-2 yrs)", "700-749", "48", "8.49", "95"],
    ["Used Car (0-2 yrs)", "700-749", "60", "8.99", "95"],
    ["Used Car (3-5 yrs)", "750-850", "36", "7.49", "95"],
    ["Used Car (3-5 yrs)", "750-850", "48", "7.99", "95"],
    ["Used Car (3-5 yrs)", "700-749", "36", "9.49", "90"],
    ["Used Car (3-5 yrs)", "700-749", "48", "9.99", "90"],
]

os.makedirs("data/csvs", exist_ok=True)
with open("data/csvs/financing_rates.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rates_data)
print("Created data/csvs/financing_rates.csv")

# ── Sample CSV: dealer fee schedule ──────────────────────────────────────────
fees_data = [
    ["Fee Type", "Amount", "Applicable When", "Notes"],
    ["Documentation Fee", "$499", "All financed purchases", "State-regulated cap may apply"],
    ["Title & Registration", "$150 - $400", "All purchases", "Varies by state DMV fees"],
    ["Dealer Prep Fee", "$299", "New vehicles only", "PDI inspection included"],
    ["GAP Insurance", "$500 - $900", "Optional add-on", "Covers difference if total loss"],
    ["Extended Warranty", "$1,200 - $3,500", "Optional add-on", "Powertrain or bumper-to-bumper"],
    ["Credit Life Insurance", "$300 - $800", "Optional add-on", "Pays off loan if borrower dies"],
    ["Paint Protection", "$299 - $799", "Optional add-on", "Ceramic coating or sealant"],
    ["Tire & Wheel Protection", "$199 - $499", "Optional add-on", "Covers road hazard damage"],
    ["Early Payoff Fee", "2% of remaining balance", "First 12 months only", "Prepayment penalty"],
    ["Late Payment Fee", "$35 or 5% of payment", "Payment >15 days late", "Whichever is greater"],
    ["NSF / Returned Payment", "$30", "Per occurrence", "Applies to checks and ACH"],
]

with open("data/csvs/fee_schedule.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(fees_data)
print("Created data/csvs/fee_schedule.csv")

# ── Sample text files acting as "PDFs" for demo purposes ─────────────────────
# (In real usage, replace with actual PDF files in data/pdfs/)

os.makedirs("data/pdfs", exist_ok=True)

loan_agreement_text = """
AUTOMOTIVE LOAN AGREEMENT - TERMS AND CONDITIONS

SECTION 1: LOAN FUNDAMENTALS

1.1 Principal Amount
The Principal Amount is the total financed amount after deducting any down payment 
and trade-in credit from the vehicle purchase price. The borrower agrees to repay 
the principal amount plus all accrued interest over the agreed loan term.

1.2 Annual Percentage Rate (APR)
The APR represents the true annual cost of the loan including all fees and interest. 
APR is determined at the time of application based on creditworthiness, loan term, 
vehicle age, and prevailing market rates. Rates are subject to change without notice 
for new applications. Approved rates are locked at the time of contract signing.

1.3 Loan Term
Loan terms are available in 24, 36, 48, 60, 72, and 84-month increments. 
Longer terms result in lower monthly payments but higher total interest paid. 
We recommend borrowers select the shortest term with an affordable monthly payment. 
Terms exceeding 60 months are not available for vehicles older than 3 model years.

1.4 Monthly Payment Calculation
Monthly payments are calculated using the standard amortization formula:
M = P[r(1+r)^n]/[(1+r)^n-1]
Where M = monthly payment, P = principal, r = monthly interest rate (APR/12), 
n = number of payments (loan term in months).

SECTION 2: CREDIT REQUIREMENTS

2.1 Minimum Credit Score
A minimum FICO score of 620 is required for loan approval. Scores below 620 may 
qualify with a qualified co-borrower. Scores above 720 qualify for our best rates.

2.2 Debt-to-Income Ratio (DTI)
Maximum allowable DTI is 50% including the proposed auto payment. DTI is calculated 
as total monthly debt obligations divided by gross monthly income. Borrowers with 
DTI between 45-50% may require larger down payments.

2.3 Employment Verification
Minimum 6 months at current employer required. Self-employed borrowers must provide 
2 years of tax returns and 3 months of bank statements. Commission-based income is 
averaged over 24 months.

2.4 Down Payment Requirements
Minimum down payment of 10% required for credit scores 650-699. 
No minimum down payment for credit scores 700+ on new vehicles. 
Used vehicles require minimum 10% down regardless of credit score.

SECTION 3: VEHICLE ELIGIBILITY

3.1 New Vehicles
All new vehicles from franchised dealers qualify. Mileage must be under 500 miles. 
MSRP cap of $150,000 applies. Exotic and limited-production vehicles may require 
additional appraisal.

3.2 Used Vehicles
Used vehicles must be model year 2015 or newer. Mileage cannot exceed 100,000 miles. 
Salvage, rebuilt, or flood-title vehicles do not qualify. Vehicles must have a clean 
Carfax or AutoCheck report.

3.3 Loan-to-Value (LTV) Ratio
LTV is calculated as loan amount divided by vehicle value (MSRP for new, 
NADA/KBB retail for used). Maximum LTV varies by credit score and vehicle type 
as published in our rate sheet. LTV over 100% (negative equity roll-in) requires 
credit score of 700 or higher.

SECTION 4: INSURANCE REQUIREMENTS

4.1 Comprehensive and Collision Coverage
Borrower must maintain comprehensive and collision insurance with deductibles 
not exceeding $1,000 for the life of the loan. Lender must be listed as lienholder 
on the insurance policy.

4.2 Proof of Insurance
Valid insurance card or declarations page must be provided at signing. 
Lapse in coverage allows lender to place force-placed insurance at borrower's expense.

4.3 GAP Insurance
GAP (Guaranteed Asset Protection) insurance is optional but strongly recommended 
for loans with LTV over 90%. GAP covers the difference between the insurance payout 
and remaining loan balance in the event of total loss or theft.

SECTION 5: PAYMENT TERMS

5.1 Due Date
First payment is due 30 days from loan origination date. Subsequent payments are 
due on the same day of each month. Borrower may select a due date between the 
1st and 28th of the month at time of origination.

5.2 Grace Period
A 15-day grace period applies to all payments. Late fees are assessed on the 
16th day after the due date.

5.3 Prepayment
Loans may be prepaid in full at any time. A prepayment penalty of 2% of the 
remaining balance applies if the loan is paid off within the first 12 months. 
No prepayment penalty applies after month 12.

5.4 Payment Methods
Payments accepted via ACH auto-pay (0.25% rate discount), online portal, 
mail (check or money order), or phone (processing fee applies). 
Cash payments accepted at branch locations only.

SECTION 6: DEFAULT AND REPOSSESSION

6.1 Definition of Default
Loan is considered in default if payment is 30 or more days past due, 
borrower allows insurance to lapse, borrower files for bankruptcy, 
or vehicle is used for commercial purposes without lender consent.

6.2 Repossession Process
Lender reserves the right to repossess the vehicle without prior notice upon default. 
Borrower will be notified of repossession and given 10 days to cure the default 
before vehicle is sold at auction.

6.3 Deficiency Balance
If auction proceeds do not cover the remaining loan balance, borrower remains 
liable for the deficiency balance. Lender may pursue legal action to collect 
deficiency balances.
"""

with open("data/pdfs/loan_agreement.txt", "w") as f:
    f.write(loan_agreement_text)
print("Created data/pdfs/loan_agreement.txt")

refinancing_guide_text = """
AUTOMOTIVE LOAN REFINANCING GUIDE

WHAT IS AUTO LOAN REFINANCING?

Refinancing your auto loan means replacing your existing loan with a new loan, 
typically to secure a lower interest rate, reduce your monthly payment, or 
change your loan term. Refinancing can save you hundreds or thousands of dollars 
over the life of your loan.

WHEN SHOULD YOU REFINANCE?

1. Your credit score has improved since original financing
If your credit score has increased by 50+ points since you took out your original 
loan, you may qualify for significantly better rates. Even a 1-2% rate reduction 
on a $25,000 loan can save $600-$1,500 over a 60-month term.

2. Interest rates have dropped in the market
If the Federal Reserve has reduced benchmark rates since your original loan, 
market auto loan rates may be substantially lower. Monitor rate trends and 
refinance when rates drop more than 1.5% below your current rate.

3. Your original loan had unfavorable terms
Dealership financing is often marked up by 1-3% above the buy rate. 
Borrowers who accepted dealer-arranged financing often benefit most from refinancing.

4. You need to lower your monthly payment
Extending your loan term through refinancing reduces monthly payments, 
though total interest paid increases.

REFINANCING ELIGIBILITY REQUIREMENTS

Minimum Credit Score: 620 (640 recommended for best rates)
Minimum Loan Balance: $7,500
Maximum Vehicle Age: 7 model years old at time of refinancing
Maximum Mileage: 120,000 miles
Minimum Months Since Original Loan: 6 months
Current Loan Status: Must be current (no 30-day lates in past 12 months)

REFINANCING PROCESS

Step 1: Check your current loan details
Gather your current loan balance, interest rate, remaining term, 
and monthly payment. Calculate your payoff amount (may differ from balance 
due to interest accrual).

Step 2: Check your credit score
Pull your credit report from AnnualCreditReport.com. Dispute any errors. 
Understand where your score stands relative to rate tiers.

Step 3: Get your vehicle value
Use NADA Guides or Kelley Blue Book to determine your vehicle's current 
retail value. Your new LTV will be based on this value.

Step 4: Apply for refinancing
Submit application with: proof of income, insurance declarations page, 
vehicle title or current registration, and 10-day payoff quote from 
current lender.

Step 5: Review and sign new loan documents
Compare new APR, monthly payment, total interest, and any fees. 
Ensure loan term aligns with your payoff goals.

REFINANCING COSTS AND FEES

Application Fee: None (we do not charge application fees)
Title Transfer Fee: $50-$150 depending on state
Prepayment Penalty on Old Loan: Check your existing loan agreement 
(typically applies only in first 12 months)
State Re-registration: May be required in some states

REFINANCING EXAMPLE

Original Loan: $28,000 at 8.9% APR, 60 months
Original Monthly Payment: $580
Total Interest Original: $6,800

Refinanced Loan: $24,500 balance at 5.9% APR, 48 months remaining
New Monthly Payment: $574
Total Interest Remaining: $3,052
Total Savings: $3,748

SPECIAL PROGRAMS

Cash-Out Refinancing
Available for vehicles with significant equity (current value exceeds 
loan balance by 20%+). Borrow against equity for other expenses. 
Maximum cash-out is $10,000 or 80% of equity, whichever is less.

Rate Reduction Program
Existing customers in good standing may qualify for a 0.5% rate reduction 
after 12 consecutive on-time payments without a full refinancing application.
"""

with open("data/pdfs/refinancing_guide.txt", "w") as f:
    f.write(refinancing_guide_text)
print("Created data/pdfs/refinancing_guide.txt")

credit_faq_text = """
AUTOMOTIVE FINANCE - FREQUENTLY ASKED QUESTIONS

Q: What credit score do I need to get approved for a car loan?
A: We approve loans for credit scores as low as 620. However, for our best interest 
rates (under 5% APR), you'll want a credit score of 720 or higher. Scores between 
650-699 qualify for standard rates with a minimum 10% down payment. If your score 
is below 620, we recommend applying with a co-borrower who has stronger credit.

Q: How much down payment do I need?
A: For customers with credit scores of 700 or higher, no minimum down payment is 
required on new vehicles. For credit scores of 650-699, we require at least 10% down. 
We always recommend putting at least 20% down to avoid being "underwater" on your loan 
(owing more than the car is worth). On a $30,000 vehicle, a 20% down payment is $6,000.

Q: What documents do I need to apply?
A: You will need: a valid government-issued photo ID, proof of income (pay stubs from 
last 30 days or 2 years tax returns if self-employed), proof of residence (utility bill 
or bank statement showing current address), proof of insurance or ability to obtain it, 
and vehicle information (VIN, make, model, year, mileage) if purchasing used.

Q: How long does the approval process take?
A: Most applications receive a credit decision within 15 minutes during business hours. 
Funding (money sent to dealer) typically occurs within 24-48 hours of receiving 
all signed documents. Same-day funding is available for applications submitted before 2 PM.

Q: Can I get pre-approved before visiting a dealership?
A: Yes. Pre-approval gives you a maximum loan amount and rate before you shop. 
Pre-approvals are valid for 30 days. Having a pre-approval strengthens your 
negotiating position at the dealership and prevents dealer financing markup.

Q: What is the difference between APR and interest rate?
A: The interest rate is the basic cost of borrowing the principal. APR (Annual Percentage 
Rate) includes the interest rate plus other loan fees and costs, expressed as a yearly rate. 
APR gives you a more complete picture of the loan's true cost. For auto loans with minimal 
fees, the APR and interest rate are often very close.

Q: What happens if I miss a payment?
A: A 15-day grace period applies. After 15 days, a late fee of $35 or 5% of the 
scheduled payment (whichever is greater) is assessed. After 30 days, the late payment 
is reported to credit bureaus. After 60 days, your account may be referred to collections. 
If you're having trouble making payments, contact us immediately — we have hardship 
programs available.

Q: Can I pay off my loan early?
A: Yes. A prepayment penalty of 2% of the remaining balance applies only if the loan 
is paid off within the first 12 months. After 12 months, you can pay off the loan 
at any time with no penalty. Making extra principal payments anytime will reduce 
your total interest paid.

Q: What is GAP insurance and do I need it?
A: GAP (Guaranteed Asset Protection) insurance covers the "gap" between what your 
auto insurance pays if your car is totaled or stolen and what you still owe on the loan. 
For example, if you owe $25,000 but the car's market value is only $20,000, 
your insurance pays $20,000 and GAP covers the remaining $5,000. GAP is strongly 
recommended if your down payment was less than 20% or your loan term is 60+ months.

Q: Can I add a co-borrower or co-signer?
A: Yes. A co-borrower shares equal responsibility for the loan and can help you 
qualify or get a better rate if they have stronger credit. A co-signer guarantees 
the loan but is not on the vehicle title. Both parties' credit scores are considered; 
we use the lower of the two middle scores for rate determination.

Q: What is LTV and why does it matter?
A: LTV stands for Loan-to-Value ratio — the loan amount divided by the vehicle's value, 
expressed as a percentage. If you borrow $22,000 to buy a $25,000 car, your LTV is 88%. 
Higher LTV means higher risk for the lender, which may result in a higher interest rate 
or require a larger down payment. Maximum LTV limits vary by credit score and vehicle type.

Q: Do you finance electric vehicles (EVs)?
A: Yes, all electric and hybrid vehicles qualify under the same terms as traditional 
vehicles. For EVs priced over $55,000, standard luxury vehicle terms apply. 
Federal tax credits can sometimes be applied as a down payment — ask your dealer 
if they offer tax credit assignment at point of sale.
"""

with open("data/pdfs/faq.txt", "w") as f:
    f.write(credit_faq_text)
print("Created data/pdfs/faq.txt")

print("\nSample data generation complete.")
print("Files created:")
print("  data/pdfs/loan_agreement.txt")
print("  data/pdfs/refinancing_guide.txt")
print("  data/pdfs/faq.txt")
print("  data/csvs/financing_rates.csv")
print("  data/csvs/fee_schedule.csv")
print("\nNote: .txt files simulate PDFs for this demo.")
print("Replace with real .pdf files for production use.")
