"""
quizzes/quiz_data.py – Financial literacy quiz questions for all 10 modules.
Questions are fact-based, sourced from RBI, NPCI, SEBI, IRDAI and Government of India.
"""
from __future__ import annotations
from typing import List, Dict

QUIZZES: Dict[str, List[Dict]] = {

    "upi_payments": [
        {
            "q": "When should you enter your UPI PIN?",
            "options": [
                "A. To receive money from someone",
                "B. To send money to someone",
                "C. To check your balance",
                "D. To update your KYC",
            ],
            "answer": "B",
            "explanation": "UPI PIN is ONLY required when SENDING money. You never need to enter your PIN to receive money. Anyone asking for your PIN to 'receive money' is a scammer. (Source: NPCI)",
        },
        {
            "q": "What is the default UPI transaction limit per transaction as per NPCI?",
            "options": [
                "A. ₹10,000",
                "B. ₹50,000",
                "C. ₹1,00,000 (₹1 lakh)",
                "D. ₹5,00,000 (₹5 lakh)",
            ],
            "answer": "C",
            "explanation": "The default UPI transaction limit is ₹1 lakh per transaction for most UPI apps. UPI Lite has a lower limit of ₹500 per transaction. (Source: NPCI)",
        },
        {
            "q": "Which of these is a government-approved UPI app?",
            "options": [
                "A. CashApp",
                "B. BHIM (Bharat Interface for Money)",
                "C. PayPal",
                "D. Venmo",
            ],
            "answer": "B",
            "explanation": "BHIM is developed by NPCI and is the official government UPI app. PhonePe, Google Pay, Paytm, and bank apps are also NPCI-approved. (Source: NPCI)",
        },
        {
            "q": "You receive an SMS saying 'Your UPI is blocked. Share OTP to unblock.' What do you do?",
            "options": [
                "A. Share the OTP to restore your account",
                "B. Call the number in the SMS",
                "C. Ignore it – it is a scam",
                "D. Reply with your Aadhaar number",
            ],
            "answer": "C",
            "explanation": "This is a classic OTP/UPI scam. Banks and NPCI never send such messages. Ignore and report to 1930 or cybercrime.gov.in. (Source: NPCI SafeUPI Campaign)",
        },
    ],

    "fraud_detection": [
        {
            "q": "What is the National Cyber Crime Helpline number in India?",
            "options": ["A. 100", "B. 1930", "C. 112", "D. 1800-111-555"],
            "answer": "B",
            "explanation": "1930 is the National Cyber Crime Helpline number. Call it immediately if you suspect financial fraud. Also report online at cybercrime.gov.in. (Source: Ministry of Home Affairs)",
        },
        {
            "q": "Which statement about investment scams is TRUE?",
            "options": [
                "A. Guaranteed 30% monthly returns are possible with right strategy",
                "B. Only SEBI-registered advisors can offer investment advice",
                "C. Telegram groups with 'insider tips' are legal",
                "D. You can verify investment returns on WhatsApp",
            ],
            "answer": "B",
            "explanation": "Only SEBI-registered investment advisors can legally provide investment advice in India. Verify at sebi.gov.in. No legitimate scheme guarantees high fixed returns. (Source: SEBI)",
        },
        {
            "q": "A 'Digital Arrest' scam involves fraudsters posing as:",
            "options": [
                "A. Bank managers requesting KYC",
                "B. Lottery companies seeking processing fees",
                "C. Fake CBI/police demanding money to avoid arrest",
                "D. Job consultants asking for registration fees",
            ],
            "answer": "C",
            "explanation": "Digital Arrest scam involves fake calls from people posing as CBI/police/enforcement agencies, threatening arrest and demanding money. Real government agencies never demand money over phone. (Source: Cyber Crime Portal)",
        },
        {
            "q": "What should you do FIRST if you get scammed online?",
            "options": [
                "A. Tell your friends and family on WhatsApp",
                "B. Call 1930 and contact your bank immediately",
                "C. Wait to see if the money comes back on its own",
                "D. Post about it on social media",
            ],
            "answer": "B",
            "explanation": "Call 1930 immediately and contact your bank to freeze the transaction. Quick action in first 24-48 hours gives the best chance of recovery. (Source: cybercrime.gov.in)",
        },
    ],

    "safe_banking": [
        {
            "q": "Under RBI rules, if you report an unauthorized transaction within 3 working days, you are liable for:",
            "options": [
                "A. Full transaction amount",
                "B. 50% of transaction amount",
                "C. ₹5,000 maximum",
                "D. Zero (₹0) – Zero Liability",
            ],
            "answer": "D",
            "explanation": "As per RBI's framework for limiting customer liability, if you report an unauthorized transaction within 3 working days, your liability is ZERO. This applies if the fraud was due to bank/third-party negligence. (Source: RBI)",
        },
        {
            "q": "What is the SAFEST way to access internet banking?",
            "options": [
                "A. Public WiFi in café for faster connection",
                "B. Shared computer at cyber café",
                "C. Your personal device on private secured internet",
                "D. Any device as long as you log out",
            ],
            "answer": "C",
            "explanation": "Always use your personal device on a secured internet connection for banking. Public WiFi and shared computers risk data theft through keyloggers and network sniffing. (Source: RBI)",
        },
        {
            "q": "You notice a loose card slot on an ATM. What should you do?",
            "options": [
                "A. Proceed with the transaction quickly",
                "B. Report it to the bank and use a different ATM",
                "C. Try to pull out the loose part to fix it",
                "D. Ask someone nearby for help",
            ],
            "answer": "B",
            "explanation": "A loose card slot could indicate a card skimmer device installed by fraudsters. Do not use that ATM – report it to the bank and use a different ATM. (Source: RBI)",
        },
    ],

    "loans_interest": [
        {
            "q": "Which type of interest rate is linked to the RBI Repo Rate for home loans?",
            "options": [
                "A. Fixed Rate",
                "B. EBLR/RLLR (External Benchmark Linked Rate)",
                "C. MIBOR Rate",
                "D. LIBOR Rate",
            ],
            "answer": "B",
            "explanation": "Most floating rate home loans are now linked to EBLR (External Benchmark Lending Rate) or RLLR (Repo-Linked Lending Rate) as mandated by RBI from October 2019. This means your rate changes when RBI changes the Repo Rate. (Source: RBI)",
        },
        {
            "q": "Which loan type typically charges the HIGHEST interest rate in India?",
            "options": [
                "A. Home Loan",
                "B. Car Loan",
                "C. Education Loan",
                "D. Credit Card outstanding balance",
            ],
            "answer": "D",
            "explanation": "Credit card outstanding balances attract 24–42% p.a. interest, far higher than home loans (8-10%), car loans (9-12%), or education loans (11-13%). Always pay your full credit card bill. (Source: RBI)",
        },
        {
            "q": "Where can you find the official EMI calculator provided by RBI?",
            "options": [
                "A. Your bank's website only",
                "B. rbi.org.in/Scripts/EMIcalculator.aspx",
                "C. sebi.gov.in",
                "D. It is not publicly available",
            ],
            "answer": "B",
            "explanation": "RBI provides a free EMI calculator at rbi.org.in/Scripts/EMIcalculator.aspx. Use it to calculate loan EMIs independently before signing any loan agreement. (Source: RBI)",
        },
    ],

    "personal_budgeting": [
        {
            "q": "In the 50-30-20 budgeting rule, what does the '20%' represent?",
            "options": [
                "A. Food and groceries",
                "B. Entertainment and wants",
                "C. Savings and investments",
                "D. Housing and rent",
            ],
            "answer": "C",
            "explanation": "In the 50-30-20 rule: 50% goes to Needs, 30% to Wants, and 20% to Savings and Investments (emergency fund, PPF, SIP, loan prepayment). (Source: RBI Financial Literacy Guide)",
        },
        {
            "q": "What is the IDEAL size of an emergency fund?",
            "options": [
                "A. 1 month of expenses",
                "B. 3–6 months of expenses",
                "C. 1 year's salary",
                "D. ₹1 lakh fixed",
            ],
            "answer": "B",
            "explanation": "An emergency fund should ideally cover 3–6 months of your essential expenses. Keep it in a liquid savings account or liquid mutual fund, NOT invested in equities. (Source: RBI Financial Literacy Centre)",
        },
        {
            "q": "Which is the BEST practice for savings automation?",
            "options": [
                "A. Save whatever is left at the end of the month",
                "B. Transfer savings on the salary day before spending",
                "C. Save only in December for tax purposes",
                "D. Keep all money in a single account",
            ],
            "answer": "B",
            "explanation": "'Pay yourself first' – automate transfers to your savings account on salary day. This ensures consistent saving before discretionary spending. (Source: RBI Financial Literacy Guide)",
        },
    ],

    "savings_emergency": [
        {
            "q": "What is the current PPF interest rate structure? (Note: verify current rate at rbi.org.in)",
            "options": [
                "A. 9.5% p.a., market-linked",
                "B. 7.1% p.a., tax-free, revised quarterly by government",
                "C. 5.5% p.a., taxable income",
                "D. 12% p.a., guaranteed",
            ],
            "answer": "B",
            "explanation": "PPF interest rate is set by the Government of India, revised quarterly. It has been at 7.1% p.a. (verify current rate at rbi.org.in or post office). Interest is completely tax-free. (Source: Ministry of Finance)",
        },
        {
            "q": "Sukanya Samriddhi Yojana (SSY) is specifically for:",
            "options": [
                "A. Senior citizens above 60 years",
                "B. Girl child (account opened before age 10)",
                "C. Any Indian citizen for tax saving",
                "D. Farmers for agricultural investment",
            ],
            "answer": "B",
            "explanation": "Sukanya Samriddhi Yojana is exclusively for the girl child. Account must be opened before the girl turns 10 years old. It offers one of the highest government-guaranteed rates. (Source: Ministry of Finance)",
        },
        {
            "q": "Where should you NOT keep your emergency fund?",
            "options": [
                "A. High-interest savings account",
                "B. Liquid mutual fund",
                "C. Equity mutual funds / stock market",
                "D. Short-term FD with sweep facility",
            ],
            "answer": "C",
            "explanation": "Emergency funds should be instantly accessible without risk of loss. Equity markets can drop 30-50% exactly when you need the money most (during job loss / medical emergency). (Source: RBI)",
        },
    ],

    "govt_schemes": [
        {
            "q": "What is the overdraft facility available under PMJDY?",
            "options": [
                "A. ₹5,000 immediately on account opening",
                "B. ₹10,000 after 6 months of satisfactory operation",
                "C. ₹1 lakh based on credit score",
                "D. No overdraft facility in PMJDY",
            ],
            "answer": "B",
            "explanation": "Under PMJDY, account holders can get an overdraft facility of up to ₹10,000 after 6 months of satisfactory account operation. This helps in financial emergencies. (Source: pmjdy.gov.in)",
        },
        {
            "q": "What is the annual premium for PMSBY (Pradhan Mantri Suraksha Bima Yojana)?",
            "options": ["A. ₹436", "B. ₹200", "C. ₹20", "D. ₹1,000"],
            "answer": "C",
            "explanation": "PMSBY provides ₹2 lakh accident insurance coverage for just ₹20 per year. PMJJBY (life insurance) costs ₹436 per year for ₹2 lakh coverage. (Source: jansuraksha.gov.in)",
        },
        {
            "q": "Under Atal Pension Yojana (APY), what is the maximum monthly pension amount?",
            "options": ["A. ₹1,000", "B. ₹3,000", "C. ₹5,000", "D. ₹10,000"],
            "answer": "C",
            "explanation": "APY provides a minimum guaranteed pension of ₹1,000–₹5,000 per month after age 60, depending on contribution amount and age of joining. (Source: jansuraksha.gov.in, PFRDA)",
        },
    ],

    "digital_security": [
        {
            "q": "What is the minimum recommended password length for banking accounts?",
            "options": ["A. 6 characters", "B. 8 characters", "C. 12 characters", "D. 4 digits"],
            "answer": "C",
            "explanation": "Cybersecurity best practices recommend minimum 12-character passwords with uppercase, lowercase, numbers, and special characters for banking accounts. Shorter passwords are more vulnerable to brute force attacks.",
        },
        {
            "q": "A fraudulent website impersonating SBI uses the URL 'statebaank.in'. This is called:",
            "options": [
                "A. Domain spoofing",
                "B. Typosquatting",
                "C. DNS poisoning",
                "D. SQL injection",
            ],
            "answer": "B",
            "explanation": "Typosquatting is when fraudsters register domains with common typos of legitimate sites (statebaank vs statebank) to steal credentials. Always type the exact URL or use bookmarks. (Source: cybercrime.gov.in)",
        },
        {
            "q": "Which permissions should you NOT grant to a mobile banking app?",
            "options": [
                "A. Camera (for cheque scanning features)",
                "B. Contacts, SMS reading",
                "C. Fingerprint authentication",
                "D. Storage (for statement downloads)",
            ],
            "answer": "B",
            "explanation": "Banking apps do NOT need access to your contacts. Malicious apps use contacts access to embarrass users or for harassment in loan scams. Read app permissions carefully before accepting. (Source: cybercrime.gov.in)",
        },
    ],

    "credit_scores": [
        {
            "q": "What is considered an excellent CIBIL credit score in India?",
            "options": ["A. 500–600", "B. 600–700", "C. 700–749", "D. 750–900"],
            "answer": "D",
            "explanation": "A CIBIL score of 750–900 is considered excellent, giving you access to the best loan interest rates and highest credit limits. The score range in India is 300–900. (Source: TransUnion CIBIL, RBI)",
        },
        {
            "q": "What is the most important factor in CIBIL score calculation?",
            "options": [
                "A. Number of bank accounts",
                "B. Payment history (never missing EMI/credit card payments)",
                "C. Monthly income",
                "D. Number of credit cards owned",
            ],
            "answer": "B",
            "explanation": "Payment history accounts for approximately 35% of your CIBIL score – the single largest factor. Always pay EMIs and credit card bills on time. Even one missed payment can impact your score. (Source: TransUnion CIBIL)",
        },
        {
            "q": "Under RBI rules, if you report a lost credit card within how many working days to get zero liability?",
            "options": [
                "A. 1 working day",
                "B. 3 working days",
                "C. 7 working days",
                "D. 30 days",
            ],
            "answer": "C",
            "explanation": "As per RBI guidelines, report a lost/stolen credit card within 7 working days to have zero liability for fraudulent transactions. Report immediately to your card issuer's 24x7 helpline. (Source: RBI)",
        },
    ],

    "investment_basics": [
        {
            "q": "What does SIP stand for in mutual fund investing?",
            "options": [
                "A. Secured Investment Plan",
                "B. Systematic Investment Plan",
                "C. Single Investment Policy",
                "D. Stock Investment Program",
            ],
            "answer": "B",
            "explanation": "SIP (Systematic Investment Plan) allows you to invest a fixed amount regularly (monthly/weekly) in a mutual fund. You can start with as little as ₹500/month. SIPs help average out market volatility (rupee-cost averaging). (Source: AMFI, SEBI)",
        },
        {
            "q": "Which regulator oversees mutual funds in India?",
            "options": ["A. RBI", "B. IRDA", "C. SEBI", "D. PFRDA"],
            "answer": "C",
            "explanation": "SEBI (Securities and Exchange Board of India) regulates all mutual funds and investment advisors in India. Verify any fund house or advisor at sebi.gov.in. (Source: SEBI)",
        },
        {
            "q": "A person claims 'guaranteed 25% monthly returns on your investment.' This is:",
            "options": [
                "A. A legitimate high-return scheme",
                "B. A SEBI-registered scheme",
                "C. An investment scam – report to SEBI",
                "D. Normal for stock market investments",
            ],
            "answer": "C",
            "explanation": "No SEBI-registered scheme guarantees fixed high returns. 'Guaranteed returns' is a classic Ponzi scheme indicator. Report to SEBI at scores.sebi.gov.in or call 1800-266-7575. (Source: SEBI)",
        },
    ],

    "insurance": [
        {
            "q": "Which type of insurance is MANDATORY by law for vehicles in India?",
            "options": [
                "A. Comprehensive insurance",
                "B. Third-party insurance",
                "C. Personal accident cover",
                "D. Engine protection cover",
            ],
            "answer": "B",
            "explanation": "Third-party motor insurance is MANDATORY under the Motor Vehicles Act. Driving without it is an offense. Comprehensive insurance additionally covers your own vehicle damage. (Source: IRDAI)",
        },
        {
            "q": "What is the 'free-look period' for insurance policies in India?",
            "options": [
                "A. 7 days to return the policy",
                "B. 15 days to return the policy if not satisfied",
                "C. 30 days to return the policy",
                "D. There is no free-look period",
            ],
            "answer": "B",
            "explanation": "IRDAI mandates a 15-day free-look period for all life insurance policies. During this period, you can return the policy if not satisfied, and get a refund of premium (minus certain deductions). (Source: IRDAI)",
        },
        {
            "q": "Under Ayushman Bharat (PM Jan Arogya Yojana), eligible families get health coverage of:",
            "options": [
                "A. ₹50,000 per year",
                "B. ₹1 lakh per year",
                "C. ₹5 lakh per year",
                "D. ₹10 lakh per year",
            ],
            "answer": "C",
            "explanation": "Ayushman Bharat PM-JAY provides health coverage of up to ₹5 lakh per family per year for secondary and tertiary hospitalization to eligible Below Poverty Line (BPL) families. (Source: Ministry of Health, IRDAI)",
        },
    ],
}


def get_quiz(module_key: str) -> List[Dict]:
    """Return quiz questions for a specific module."""
    return QUIZZES.get(module_key, [])


def get_all_modules() -> List[str]:
    """Return all quiz module keys."""
    return list(QUIZZES.keys())
