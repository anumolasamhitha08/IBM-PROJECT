"""
rag/knowledge_base.py – Extended trusted financial knowledge base for FinSakhi.
Sources: RBI, NPCI, CyberCrime Portal, PMJDY, SEBI, IRDAI and Government of India.
All facts are sourced from public official documents.
"""
from __future__ import annotations
from typing import List, Dict

# ── SOURCE REGISTRY ────────────────────────────────────────────────────────────
SOURCE_REGISTRY = {
    "rbi.org.in":          {"name": "Reserve Bank of India",           "url": "https://www.rbi.org.in/",              "category": "Banking & Monetary Policy"},
    "npci.org.in":         {"name": "NPCI – National Payments Corp.",  "url": "https://www.npci.org.in/",             "category": "Digital Payments"},
    "cybercrime.gov.in":   {"name": "Indian Cyber Crime Portal",       "url": "https://cybercrime.gov.in/",           "category": "Cyber Security"},
    "pmjdy.gov.in":        {"name": "PM Jan Dhan Yojana",              "url": "https://pmjdy.gov.in/",                "category": "Government Schemes"},
    "sebi.gov.in":         {"name": "SEBI – Securities & Exchange Bd", "url": "https://www.sebi.gov.in/",             "category": "Investments & Securities"},
    "irdai.gov.in":        {"name": "IRDAI – Insurance Regulatory",    "url": "https://irdai.gov.in/",                "category": "Insurance"},
    "india.gov.in":        {"name": "Government of India Portal",      "url": "https://india.gov.in/",                "category": "Government Schemes"},
    "pmkisan.gov.in":      {"name": "PM Kisan Samman Nidhi",           "url": "https://pmkisan.gov.in/",              "category": "Agriculture Schemes"},
    "jansuraksha.gov.in":  {"name": "Jan Suraksha Schemes",            "url": "https://jansuraksha.gov.in/",          "category": "Social Security"},
}


KNOWLEDGE_BASE: List[Dict] = [

    # ═══════════════════════════════════════════════════════════════
    # MODULE 1: UPI AND DIGITAL PAYMENTS
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "upi_001", "module": "upi_payments", "language": "en",
        "source": "npci.org.in", "source_date": "2024-01",
        "content": """UPI (Unified Payments Interface) is a real-time payment system developed by NPCI (National Payments Corporation of India). It enables instant money transfers 24x7, 365 days via mobile.

HOW TO SEND MONEY VIA UPI:
1. Open your UPI-enabled app (BHIM, PhonePe, Google Pay, Paytm, bank app)
2. Select 'Send Money' or 'Pay'
3. Enter recipient's UPI ID (e.g., name@upi) or scan QR code
4. Enter the amount
5. Add a remark (optional)
6. Enter your 4–6 digit UPI PIN to authorize
7. Transaction completes within seconds

UPI TRANSACTION LIMITS (as per NPCI):
- Default: ₹1 lakh per transaction
- UPI 123PAY (feature phones): ₹5,000 per transaction
- UPI LITE (small payments): ₹500 per transaction, ₹2,000 wallet limit

UPI APPS APPROVED BY NPCI: BHIM, PhonePe, Google Pay, Paytm, Amazon Pay, and 50+ bank apps.

Source: NPCI (npci.org.in)""",
    },
    {
        "id": "upi_safety_001", "module": "upi_payments", "language": "en",
        "source": "npci.org.in", "source_date": "2024-01",
        "content": """UPI SAFETY RULES – CRITICAL INFORMATION:

NEVER SHARE YOUR UPI PIN:
- UPI PIN is only required to SEND money, NEVER to receive
- No bank, NPCI, or app will ever ask for your PIN
- If someone asks for your PIN, it is a SCAM

SAFE UPI PRACTICES:
1. Never click on links received via SMS/WhatsApp claiming UPI rewards
2. Always verify recipient UPI ID before sending
3. Collect requests from unknown persons should be REJECTED
4. Never scan QR codes sent by strangers to 'receive' money
5. Do not use UPI on unsecured public WiFi
6. Set a daily transaction limit in your app settings
7. Enable 2-factor authentication where available
8. Regularly check your transaction history

RED FLAGS:
- "Enter PIN to receive money" – SCAM
- "Your UPI is blocked, share OTP to unblock" – SCAM
- Requests for remote access to verify UPI – SCAM

Report UPI fraud: Call 1930 or visit cybercrime.gov.in
NPCI dispute resolution: npci.org.in

Source: NPCI SafeUPI Campaign (npci.org.in)""",
    },
    {
        "id": "upi_hi_001", "module": "upi_payments", "language": "hi",
        "source": "npci.org.in", "source_date": "2024-01",
        "content": """UPI (एकीकृत भुगतान इंटरफेस) NPCI द्वारा विकसित एक रियल-टाइम भुगतान प्रणाली है।

UPI से पैसे भेजने के तरीके:
1. अपना UPI ऐप खोलें (BHIM, PhonePe, Google Pay)
2. 'पैसे भेजें' चुनें
3. प्राप्तकर्ता का UPI ID या मोबाइल नंबर डालें
4. राशि दर्ज करें
5. UPI PIN डालकर अनुमोदित करें

सुरक्षा नियम:
- अपना UPI PIN कभी किसी के साथ साझा न करें
- PIN केवल पैसे भेजने के लिए डालें, पैसे पाने के लिए नहीं
- अनजान व्यक्तियों के Collect Request को अस्वीकार करें
- UPI धोखाधड़ी रिपोर्ट करें: 1930 पर कॉल करें

स्रोत: NPCI (npci.org.in)""",
    },
    {
        "id": "upi_te_001", "module": "upi_payments", "language": "te",
        "source": "npci.org.in", "source_date": "2024-01",
        "content": """UPI (యూనిఫైడ్ పేమెంట్స్ ఇంటర్‌ఫేస్) NPCI అభివృద్ధి చేసిన రియల్-టైమ్ పేమెంట్ సిస్టమ్.

UPI ద్వారా డబ్బు పంపడం:
1. UPI యాప్ తెరవండి (BHIM, PhonePe, Google Pay)
2. 'డబ్బు పంపండి' ఎంచుకోండి
3. గ్రహీత UPI ID లేదా మొబైల్ నంబర్ నమోదు చేయండి
4. మొత్తం నమోదు చేయండి
5. UPI PIN తో అనుమతించండి

భద్రతా నియమాలు:
- మీ UPI PIN ఎవరితోనూ పంచుకోకండి
- PIN కేవలం డబ్బు పంపేందుకు మాత్రమే
- తెలియని వ్యక్తుల Collect అభ్యర్థనలను తిరస్కరించండి
- UPI మోసం నివేదించండి: 1930 కి కాల్ చేయండి

మూలం: NPCI (npci.org.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 2: ONLINE FRAUD AND SCAM DETECTION
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "scam_001", "module": "fraud_detection", "language": "en",
        "source": "cybercrime.gov.in", "source_date": "2024-03",
        "content": """COMMON FINANCIAL SCAMS IN INDIA (2024):

1. OTP SCAM: Fraudster calls posing as bank/NPCI, asks for OTP. NEVER share OTP.

2. KYC UPDATE SCAM: Fake call saying 'Your account will be blocked, update KYC by sharing OTP'. Banks NEVER ask for OTP over phone.

3. LOTTERY/PRIZE SCAM: "You've won ₹50 lakh lottery, pay ₹5,000 processing fee." Legitimate lotteries never ask for upfront fees.

4. INVESTMENT SCAM: "Guaranteed 40% monthly returns." SEBI-registered schemes never promise fixed guaranteed returns.

5. COURIER SCAM: Fake call from 'customs/courier', saying a package is held and asking for payment.

6. DIGITAL ARREST SCAM: Fake call from 'CBI/police' about a crime, demands money to avoid arrest.

7. JOB OFFER SCAM: High-paying job requiring registration fee or training deposit.

8. LOAN APP SCAM: Instant loan apps that steal phone data and harass contacts.

9. ROMANCE SCAM: Online friendship leading to requests for money transfers.

10. SCREEN SHARING SCAM: "Share your screen to verify UPI" — gives fraudster full access.

HOW TO VERIFY:
- Call your bank's official number (on card/passbook)
- Check SEBI registration: sebi.gov.in/sebiweb/other/OtherAction.do
- Verify mutual funds: amfiindia.com

REPORT IMMEDIATELY:
- National Cyber Crime Helpline: 1930
- Online: cybercrime.gov.in
- RBI Banking Ombudsman: bankingombudsman.rbi.org.in

Source: Ministry of Home Affairs, Cyber Crime Portal (cybercrime.gov.in)""",
    },
    {
        "id": "scam_hi_001", "module": "fraud_detection", "language": "hi",
        "source": "cybercrime.gov.in", "source_date": "2024-03",
        "content": """भारत में आम वित्तीय धोखाधड़ी:

1. OTP धोखाधड़ी: बैंक बनकर OTP मांगना। OTP कभी साझा न करें।
2. KYC अपडेट धोखाधड़ी: "खाता बंद होगा, OTP दें" - यह घोटाला है।
3. लॉटरी घोटाला: "आप ₹50 लाख जीते हैं, ₹5,000 शुल्क दें" - कभी भुगतान न करें।
4. निवेश घोटाला: "गारंटीड 40% रिटर्न" - SEBI पंजीकृत योजनाएं कभी गारंटी नहीं देतीं।
5. डिजिटल अरेस्ट: फर्जी CBI/पुलिस कॉल, पैसे मांगना।

कैसे सुरक्षित रहें:
- बैंक का आधिकारिक नंबर (कार्ड पर लिखा) पर कॉल करें
- SEBI पर निवेश सत्यापित करें: sebi.gov.in

तुरंत रिपोर्ट करें:
- साइबर क्राइम हेल्पलाइन: 1930
- ऑनलाइन: cybercrime.gov.in

स्रोत: साइबर क्राइम पोर्टल (cybercrime.gov.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 3: SAFE BANKING PRACTICES
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "banking_001", "module": "safe_banking", "language": "en",
        "source": "rbi.org.in", "source_date": "2024-01",
        "content": """SAFE BANKING PRACTICES – RBI GUIDELINES:

INTERNET BANKING SAFETY:
1. Always use official bank website (verify https:// and padlock icon)
2. Never access net banking on public computers or WiFi
3. Use virtual keyboard for password entry when available
4. Log out completely after each session
5. Never save passwords in browser on shared devices
6. Register mobile number for transaction alerts

DEBIT/CREDIT CARD SAFETY:
1. Never share CVV, card number, or expiry date over phone/email
2. Cover keypad when entering PIN at ATM
3. Check ATM for skimmer devices (loose card slot, extra cameras)
4. Use contactless payments where available for small amounts
5. Set international transaction limits when not travelling abroad
6. Report lost/stolen card immediately: call bank's 24x7 helpline

ATM SAFETY:
1. Use ATMs inside bank branches when possible
2. Avoid ATMs in isolated locations, especially at night
3. Cancel transaction if ATM behaves strangely
4. Count cash before leaving ATM
5. Do not accept help from strangers at ATM

ACCOUNT MONITORING:
- Set up SMS/email alerts for all transactions
- Review statements monthly
- Immediately report unauthorized transactions
- Use account aggregator apps carefully

RBI Customer Rights: If bank refuses to compensate for unauthorized transaction reported within 3 days, you are eligible for zero liability.

Source: RBI (rbi.org.in/Scripts/FinancialEducation.aspx)""",
    },
    {
        "id": "banking_hi_001", "module": "safe_banking", "language": "hi",
        "source": "rbi.org.in", "source_date": "2024-01",
        "content": """सुरक्षित बैंकिंग अभ्यास - RBI दिशानिर्देश:

इंटरनेट बैंकिंग सुरक्षा:
- हमेशा बैंक की आधिकारिक वेबसाइट का उपयोग करें (https:// देखें)
- सार्वजनिक WiFi पर नेट बैंकिंग न करें
- हर सत्र के बाद लॉगआउट करें
- ब्राउजर में पासवर्ड सेव न करें

कार्ड सुरक्षा:
- ATM PIN डालते समय कीपैड ढकें
- CVV, कार्ड नंबर फोन पर कभी न बताएं
- खोया/चोरी कार्ड तुरंत ब्लॉक करें

RBI अधिकार: 3 दिन में रिपोर्ट किए गए अनधिकृत लेनदेन पर जीरो दायित्व।

स्रोत: RBI (rbi.org.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 4: LOANS AND INTEREST RATES
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "loans_001", "module": "loans_interest", "language": "en",
        "source": "rbi.org.in", "source_date": "2024-06",
        "content": """LOANS AND INTEREST RATES IN INDIA (Indicative rates, verify current rates at rbi.org.in):

HOME LOANS (Indicative 2024):
- Public sector banks: 8.40%–9.15% p.a.
- Private banks: 8.75%–10.50% p.a.
- Interest type: Usually floating (linked to EBLR or RLLR)
- Processing fee: 0.25%–1% of loan amount
- Maximum tenure: 30 years

PERSONAL LOANS (Indicative 2024):
- Banks: 10.50%–21% p.a.
- NBFCs: 12%–30% p.a.
- Repayment: 1–5 years
- Watch out for hidden charges

CAR LOANS (Indicative 2024):
- New cars: 8.75%–12% p.a.
- Used cars: 12%–18% p.a.

EDUCATION LOANS:
- Up to ₹4 lakh: No collateral, ~11.15%–12.85% p.a.
- Above ₹7.5 lakh: Collateral required
- Vidya Lakshmi Portal: vidyalakshmi.co.in

CREDIT CARDS:
- Interest rate: 24%–42% p.a. (2–3.5% per month)
- Avoid revolving credit – always pay full bill

KEY POINTS:
- RBI Repo Rate: Check current rate at rbi.org.in
- Compare at least 3 lenders before choosing
- Read fine print for prepayment penalties
- EMI calculator: rbi.org.in/Scripts/EMIcalculator.aspx
- Report loan harassment: Call 14448 (RBI Helpline)

IMPORTANT: Interest rates change regularly. Always verify current rates directly with your bank or at rbi.org.in before taking any loan.

Source: RBI (rbi.org.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 5: PERSONAL BUDGETING
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "budget_001", "module": "personal_budgeting", "language": "en",
        "source": "rbi.org.in", "source_date": "2023-12",
        "content": """PERSONAL BUDGETING FOR INDIANS:

THE 50-30-20 RULE (RBI Financial Literacy Guide):
- 50% → Needs: Rent/EMI, food, utilities, transport, insurance
- 30% → Wants: Dining out, entertainment, shopping, subscriptions
- 20% → Savings & Investments: Emergency fund, PPF, SIP, loan prepayment

STEP-BY-STEP BUDGET CREATION:
1. Calculate net monthly income (salary after all deductions)
2. List all fixed expenses (rent, EMIs, insurance premiums)
3. Track variable expenses for 2-3 months (use a notebook or free app)
4. Identify areas to reduce spending
5. Automate savings transfers on salary day (before spending)
6. Review budget every month

PRACTICAL TIPS FOR INDIA:
- Use free apps: Money Manager, Walnut, ETMONEY Planner
- Separate accounts: one for expenses, one for savings
- Set a 'no spend' day each week
- Use cash for discretionary spending to feel the expense
- Grocery: Plan meals weekly, buy in bulk for non-perishables

EMERGENCY FUND GOAL:
- Minimum: 3 months of expenses
- Ideal: 6 months of expenses
- Keep in: Liquid fund or high-interest savings account

Source: RBI Financial Literacy Centre (rbi.org.in)""",
    },
    {
        "id": "budget_hi_001", "module": "personal_budgeting", "language": "hi",
        "source": "rbi.org.in", "source_date": "2023-12",
        "content": """व्यक्तिगत बजट बनाने का तरीका:

50-30-20 नियम:
- 50% → जरूरतें: किराया, EMI, खाना, बिजली
- 30% → इच्छाएं: बाहर खाना, मनोरंजन, खरीदारी
- 20% → बचत और निवेश: आपातकालीन निधि, PPF, SIP

बजट कैसे बनाएं:
1. मासिक आय गणना करें
2. सभी निश्चित खर्च लिखें
3. 2-3 महीने परिवर्तनशील खर्च ट्रैक करें
4. बचत को वेतन दिन स्वचालित करें
5. हर महीने समीक्षा करें

आपातकालीन निधि: कम से कम 3-6 महीने के खर्च

स्रोत: RBI वित्तीय साक्षरता केंद्र (rbi.org.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 6: SAVINGS AND EMERGENCY FUNDS
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "savings_001", "module": "savings_emergency", "language": "en",
        "source": "india.gov.in", "source_date": "2024-04",
        "content": """SAVINGS OPTIONS IN INDIA (Indicative rates – verify at rbi.org.in or respective institution):

GOVERNMENT-BACKED SAVINGS (Low risk):
1. PPF (Public Provident Fund):
   - Interest: 7.1% p.a. (tax-free, revised quarterly)
   - Lock-in: 15 years (partial withdrawal after 7 years)
   - Tax benefit: Sec 80C, maturity amount tax-free
   - Available at: Post office, SBI, major banks

2. Sukanya Samriddhi Yojana (girl child):
   - Interest: 8.2% p.a. (revised quarterly)
   - For girls under 10 years, matures at 21 years
   - Tax benefit: Sec 80C

3. Senior Citizen Savings Scheme (SCSS):
   - Interest: 8.2% p.a. (for age 60+)
   - Maximum: ₹30 lakh
   - Available at: Post office, authorized banks

4. National Savings Certificate (NSC):
   - Interest: 7.7% p.a. (5-year scheme)
   - Tax benefit: Sec 80C

5. Post Office Time Deposit:
   - 1 year: ~6.9% p.a., 5 year: ~7.5% p.a. (verify current rates)

MARKET-LINKED SAVINGS:
- SIP in Mutual Funds: Start with ₹500/month
- NPS (National Pension System): Market-linked + tax benefit under 80CCD(1B)

EMERGENCY FUND:
- Keep 3-6 months of expenses in liquid/savings account
- Do NOT invest emergency fund in equities
- Liquid mutual funds offer better returns than savings accounts

IMPORTANT: All rates are indicative. Check current rates at rbi.org.in, nsiindia.gov.in or your bank before investing.

Source: India.gov.in, Ministry of Finance""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 7: GOVERNMENT FINANCIAL SCHEMES
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "pmjdy_001", "module": "govt_schemes", "language": "en",
        "source": "pmjdy.gov.in", "source_date": "2024-01",
        "content": """PRADHAN MANTRI JAN DHAN YOJANA (PMJDY):

FEATURES (as per pmjdy.gov.in):
- Zero-balance savings account at any bank or Business Correspondent
- RuPay debit card with ₹2 lakh accident insurance (if account holder is active)
- ₹30,000 life insurance for accounts opened between 15 Aug 2014 – 31 Jan 2015
- Overdraft facility up to ₹10,000 (for accounts with 6-month satisfactory operation)
- Direct Benefit Transfer (DBT) eligible

ELIGIBILITY: Any Indian citizen aged 10 years and above without a bank account

HOW TO APPLY:
1. Visit nearest bank branch or Business Correspondent (Bank Mitra)
2. Carry: Aadhaar card OR voter ID / passport / NREGA card
3. Fill Form 1 (account opening form)
4. Account opened same day (or within 10 days for verification)

PMJDY STATISTICS (as of 2024): 530+ million accounts opened
(Verify current data at pmjdy.gov.in)

Source: PM Jan Dhan Yojana (pmjdy.gov.in)""",
    },
    {
        "id": "govt_schemes_001", "module": "govt_schemes", "language": "en",
        "source": "jansuraksha.gov.in", "source_date": "2024-04",
        "content": """GOVERNMENT INSURANCE & PENSION SCHEMES:

1. PMJJBY (Pradhan Mantri Jeevan Jyoti Bima Yojana):
   - Life insurance: ₹2 lakh coverage
   - Annual premium: ₹436 (auto-deducted from bank account)
   - Eligibility: 18–50 years, savings bank account
   - Apply: Any bank branch or jansuraksha.gov.in

2. PMSBY (Pradhan Mantri Suraksha Bima Yojana):
   - Accident insurance: ₹2 lakh (death/permanent disability)
   - Annual premium: ₹20
   - Eligibility: 18–70 years, savings bank account

3. APY (Atal Pension Yojana):
   - Pension: ₹1,000–₹5,000/month after age 60
   - Government co-contributes 50% (up to ₹1,000/year) for eligible subscribers
   - Eligibility: 18–40 years, unorganized sector workers
   - Enroll: Any bank branch or nps.nsdl.com

4. PM Kisan Samman Nidhi:
   - ₹6,000/year (₹2,000 every 4 months) for small/marginal farmers
   - Eligibility: Farmers with up to 2 hectares of land
   - Apply: pmkisan.gov.in or nearest CSC

5. PM Awas Yojana (PMAY):
   - Housing subsidy for economically weaker sections
   - Credit-linked subsidy under PMAY-Urban/Rural
   - Apply: pmaymis.gov.in

Source: Jan Suraksha (jansuraksha.gov.in), Ministry of Finance""",
    },
    {
        "id": "govt_hi_001", "module": "govt_schemes", "language": "hi",
        "source": "pmjdy.gov.in", "source_date": "2024-01",
        "content": """सरकारी वित्तीय योजनाएं:

1. PM Jan Dhan Yojana (PMJDY):
   - शून्य-शेष बचत खाता
   - RuPay डेबिट कार्ड + ₹2 लाख दुर्घटना बीमा
   - ₹10,000 ओवरड्राफ्ट सुविधा (6 महीने बाद)
   - पात्रता: 10 वर्ष से ऊपर का कोई भी भारतीय नागरिक
   - आवेदन: किसी भी बैंक शाखा या Bank Mitra

2. PMJJBY: ₹2 लाख जीवन बीमा, ₹436 वार्षिक प्रीमियम

3. PMSBY: ₹2 लाख दुर्घटना बीमा, मात्र ₹20 वार्षिक प्रीमियम

4. APY (अटल पेंशन योजना): 60 वर्ष के बाद ₹1,000–₹5,000 मासिक पेंशन

5. PM Kisan: किसानों को ₹6,000/वर्ष

स्रोत: pmjdy.gov.in, jansuraksha.gov.in""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 8: DIGITAL BANKING SECURITY
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "cyber_crime_001", "module": "digital_security", "language": "en",
        "source": "cybercrime.gov.in", "source_date": "2024-03",
        "content": """DIGITAL BANKING SECURITY – COMPREHENSIVE GUIDE:

PASSWORD SECURITY:
- Use minimum 12-character passwords with uppercase, lowercase, numbers, symbols
- Never reuse banking passwords for other sites
- Change passwords every 3 months
- Use a password manager (not browser storage for banking)
- Enable two-factor authentication (2FA) wherever available

PHISHING PREVENTION:
- Banks never send login links via SMS/email/WhatsApp
- Always type bank URL directly in browser
- Check SSL certificate (padlock + correct bank domain)
- Beware of typosquat domains (e.g., statebaank.com vs sbi.co.in)

MOBILE BANKING:
- Download apps only from official App Store/Play Store
- Check developer name carefully (should be official bank name)
- Deny unnecessary permissions (contacts, location) to banking apps
- Enable biometric authentication where available
- Do not root/jailbreak your phone

DEVICE SECURITY:
- Keep OS and apps updated for security patches
- Use reputable antivirus on your device
- Encrypt your device storage
- Lock your phone with PIN/biometric

WHAT TO DO IF COMPROMISED:
1. Immediately call your bank's 24x7 helpline
2. Call 1930 (National Cyber Crime Helpline)
3. Change all passwords from a secure device
4. File report at cybercrime.gov.in
5. Freeze your account temporarily if needed

Source: Indian Cyber Crime Coordination Centre (cybercrime.gov.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 9: CREDIT CARDS AND CREDIT SCORES
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "credit_001", "module": "credit_scores", "language": "en",
        "source": "rbi.org.in", "source_date": "2024-02",
        "content": """CREDIT CARDS AND CREDIT SCORES IN INDIA:

CREDIT SCORE (CIBIL Score):
- Range: 300–900 (higher is better)
- Excellent: 750–900 (best loan rates)
- Good: 700–749 (good loan eligibility)
- Fair: 650–699 (limited options)
- Poor: Below 650 (difficult to get loans)

HOW TO CHECK YOUR CIBIL SCORE:
- Free once a year at: cibil.com
- Also available on: BankBazaar, Paytm, Google Pay
- RBI mandates free credit report once per year

HOW CREDIT SCORE IS CALCULATED:
- Payment history: 35% (most important – never miss payments)
- Credit utilization: 30% (keep below 30% of limit)
- Length of credit history: 15%
- New credit inquiries: 10%
- Credit mix: 10%

CREDIT CARD SAFETY RULES:
- Always pay FULL outstanding, not minimum amount
- Minimum payment leads to 24–42% annual interest
- Set auto-debit for at least minimum amount (to avoid late fees)
- Never exceed 30% of credit limit
- Report lost card within 7 working days for zero liability (RBI rule)
- Never share card details, CVV, or OTP over phone

BUILDING CREDIT:
- Secured credit card (against FD) is good for beginners
- Maintain credit utilization below 30%
- Never close old credit cards (reduces average history)

Source: RBI (rbi.org.in), TransUnion CIBIL""",
    },

    # ═══════════════════════════════════════════════════════════════
    # MODULE 10: BASIC INVESTMENT AWARENESS
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "investment_001", "module": "investment_basics", "language": "en",
        "source": "sebi.gov.in", "source_date": "2024-01",
        "content": """BASIC INVESTMENT AWARENESS – SEBI GUIDELINES:

INVESTMENT BASICS:
- All investments carry risk; higher returns = higher risk
- Never invest borrowed money in equity markets
- Diversify: Don't put all eggs in one basket
- Invest for long term to reduce market volatility impact

SEBI-REGULATED INVESTMENTS:
1. Mutual Funds:
   - Pooled investment managed by SEBI-registered fund houses
   - SIP (Systematic Investment Plan): Start with ₹500/month
   - ELSS (Equity Linked Savings Scheme): Tax benefit under Sec 80C
   - Check fund ratings at: mfcentral.com or amfiindia.com

2. Direct Equity (Stock Market):
   - Open demat + trading account with SEBI-registered broker
   - NSE: nseindia.com | BSE: bseindia.com
   - Never trade based on tips from WhatsApp/Telegram groups
   - Always do fundamental research or consult SEBI-registered advisor

3. NPS (National Pension System):
   - Long-term retirement savings
   - Additional ₹50,000 tax benefit under Sec 80CCD(1B)
   - Enroll at nps.nsdl.com or bank branches

INVESTMENT SCAM RED FLAGS:
- "Guaranteed 20%+ returns" – Illegal and impossible in legitimate markets
- "Invest today only, offer expires in 24 hours" – Pressure tactic
- Unregistered advisors – Always verify SEBI registration
- Verify advisor at: sebi.gov.in/sebiweb/other/OtherAction.do

SEBI COMPLAINT: scores.sebi.gov.in
SEBI Investor Helpline: 1800-266-7575

IMPORTANT: Past returns do not guarantee future performance. Consult a SEBI-registered investment advisor before investing.

Source: SEBI (sebi.gov.in), AMFI (amfiindia.com)""",
    },
    {
        "id": "investment_hi_001", "module": "investment_basics", "language": "hi",
        "source": "sebi.gov.in", "source_date": "2024-01",
        "content": """निवेश जागरूकता - SEBI दिशानिर्देश:

मूल सिद्धांत:
- सभी निवेशों में जोखिम होता है - ज्यादा रिटर्न = ज्यादा जोखिम
- कर्ज के पैसे कभी शेयर बाजार में न लगाएं
- विविधीकरण: एक ही जगह सारा पैसा न लगाएं

SEBI-विनियमित निवेश:
1. म्यूचुअल फंड: SIP से ₹500/माह से शुरू करें
2. ELSS: धारा 80C के तहत कर लाभ
3. NPS: सेवानिवृत्ति बचत + 80CCD(1B) लाभ

निवेश घोटाले की पहचान:
- "गारंटीड 20%+ रिटर्न" - यह धोखा है
- बिना SEBI पंजीकरण के सलाहकार
- SEBI शिकायत: scores.sebi.gov.in
- SEBI हेल्पलाइन: 1800-266-7575

स्रोत: SEBI (sebi.gov.in)""",
    },

    # ═══════════════════════════════════════════════════════════════
    # INSURANCE (IRDAI)
    # ═══════════════════════════════════════════════════════════════
    {
        "id": "insurance_001", "module": "insurance", "language": "en",
        "source": "irdai.gov.in", "source_date": "2024-03",
        "content": """INSURANCE IN INDIA – IRDAI GUIDELINES:

TYPES OF INSURANCE:
1. LIFE INSURANCE:
   - Term Life: Pure protection (death benefit only), lowest premium
   - Endowment: Protection + savings (lower returns, not recommended for pure investment)
   - ULIP: Insurance + market investment (high charges, verify before buying)
   - Recommended: Buy term life with sum assured = 10-20× annual income

2. HEALTH INSURANCE:
   - Individual/Family floater plans
   - Look for: Cashless hospitals, pre-existing disease coverage after waiting period
   - Minimum recommended: ₹5 lakh per person for urban areas
   - PM Arogya: Up to ₹5 lakh for BPL families under Ayushman Bharat

3. MOTOR INSURANCE:
   - Third-party insurance: MANDATORY as per law
   - Comprehensive: Recommended for own vehicle damage
   - Renew before expiry – gap in insurance makes vehicle illegal to drive

IRDAI CONSUMER RIGHTS:
- Claim settlement ratio: Check on IRDAI website irdai.gov.in
- Grievance: Call 155255 or visit irdai.gov.in/IIRDAI/NOIDAOFFICE/CONSUMERAFFAIRS/0/21
- Insurance Ombudsman: ecoi.co.in

BUYING INSURANCE SAFELY:
1. Buy only from IRDAI-registered insurers (verify at irdai.gov.in)
2. Never pay cash to agents
3. Get original policy document
4. Free-look period: 15 days to return policy if not satisfied
5. Never surrender old life insurance policy without calculating loss

Source: IRDAI (irdai.gov.in)""",
    },
]


def get_module_metadata() -> Dict[str, Dict]:
    """Return metadata for each financial literacy module."""
    return {
        "upi_payments": {
            "title": "UPI & Digital Payments",
            "icon": "📱",
            "description": "Learn UPI payments, BHIM, PhonePe, Google Pay, and digital payment safety",
            "source": "NPCI",
            "url": "https://www.npci.org.in/",
        },
        "fraud_detection": {
            "title": "Online Fraud & Scam Detection",
            "icon": "🚨",
            "description": "Identify and report OTP scams, lottery fraud, investment scams, and more",
            "source": "Cyber Crime Portal",
            "url": "https://cybercrime.gov.in/",
        },
        "safe_banking": {
            "title": "Safe Banking Practices",
            "icon": "🏦",
            "description": "Internet banking security, ATM safety, card protection guidelines",
            "source": "RBI",
            "url": "https://www.rbi.org.in/",
        },
        "loans_interest": {
            "title": "Loans & Interest Rates",
            "icon": "💳",
            "description": "Home loans, personal loans, car loans, education loans – rates and tips",
            "source": "RBI",
            "url": "https://www.rbi.org.in/",
        },
        "personal_budgeting": {
            "title": "Personal Budgeting",
            "icon": "📊",
            "description": "50-30-20 rule, expense tracking, monthly budget planning",
            "source": "RBI",
            "url": "https://www.rbi.org.in/",
        },
        "savings_emergency": {
            "title": "Savings & Emergency Funds",
            "icon": "🐷",
            "description": "PPF, Sukanya Samriddhi, SCSS, NSC, emergency fund building",
            "source": "Government of India",
            "url": "https://india.gov.in/",
        },
        "govt_schemes": {
            "title": "Government Financial Schemes",
            "icon": "🏛️",
            "description": "PMJDY, PMJJBY, PMSBY, APY, PM Kisan, PMAY and more",
            "source": "PMJDY Portal",
            "url": "https://pmjdy.gov.in/",
        },
        "digital_security": {
            "title": "Digital Banking Security",
            "icon": "🔐",
            "description": "Password security, phishing prevention, mobile banking safety",
            "source": "Cyber Crime Portal",
            "url": "https://cybercrime.gov.in/",
        },
        "credit_scores": {
            "title": "Credit Cards & Credit Scores",
            "icon": "💎",
            "description": "CIBIL score, credit card safety, building and improving credit",
            "source": "RBI",
            "url": "https://www.rbi.org.in/",
        },
        "investment_basics": {
            "title": "Basic Investment Awareness",
            "icon": "📈",
            "description": "Mutual funds, SIP, NPS, SEBI rules, avoiding investment scams",
            "source": "SEBI",
            "url": "https://www.sebi.gov.in/",
        },
        "insurance": {
            "title": "Insurance Awareness",
            "icon": "🛡️",
            "description": "Life, health, motor insurance – IRDAI guidelines and consumer rights",
            "source": "IRDAI",
            "url": "https://irdai.gov.in/",
        },
    }
