# 💰 FinSakhi – AI Financial Literacy Assistant

> **Production-quality AI agent for Digital Financial Literacy** — Powered by **IBM Granite LLM** on WatsonX.

FinSakhi is a Streamlit-based, RAG-powered AI assistant that helps Indian users understand digital financial concepts, avoid scams, and safely use digital banking — in English, Hindi, and Telugu.

---

## 🏗️ Architecture Overview

```
User → Streamlit UI (app.py)
          │
          ├─ Rate Limiter (middleware/rate_limiter.py)
          ├─ Input Guardrails (guardrails/input_guardrails.py)
          │
          ├─ Supervisor Agent (agents/supervisor_agent.py)
          │      └─ Routes to Specialized Agents:
          │           ├─ UPISafetyAgent
          │           ├─ ScamDetectionAgent
          │           ├─ BudgetPlanningAgent
          │           ├─ GovernmentSchemesAgent
          │           ├─ MultilingualAgent
          │           └─ FinancialLiteracyAgent
          │
          ├─ RAG Pipeline (rag/rag_pipeline.py)
          │      ├─ ChromaDB Vector Store
          │      └─ Knowledge Base (rag/knowledge_base.py)
          │           Sources: RBI, NPCI, SEBI, IRDAI, PMJDY, Cyber Crime Portal
          │
          ├─ IBM Granite LLM (llm_client.py)
          │
          ├─ Output Guardrails (guardrails/output_guardrails.py)
          │
          └─ Monitoring + DB (monitoring/ + database.py)
```

---

## ✨ Features

### 🤖 AI Assistant
- Answers financial literacy questions using **Retrieval-Augmented Generation (RAG)**
- Powered by **IBM Granite LLM** (ibm/granite-3-3-8b-instruct)
- Falls back to RAG document retrieval when LLM is not configured
- **Never fabricates financial rates, policies, or statistics**
- Shows "N/A" or redirects to official sources when information is unavailable

### 🌐 Multilingual Support
- **English**, **Hindi (हिन्दी)**, **Telugu (తెలుగు)**
- Automatic language detection
- Dedicated multilingual knowledge base entries

### 📚 10 Financial Literacy Modules (with Quizzes)
1. 📱 UPI & Digital Payments
2. 🚨 Online Fraud & Scam Detection
3. 🏦 Safe Banking Practices
4. 💳 Loans & Interest Rates
5. 📊 Personal Budgeting
6. 🐷 Savings & Emergency Funds
7. 🏛️ Government Financial Schemes
8. 🔐 Digital Banking Security
9. 💎 Credit Cards & Credit Scores
10. 📈 Basic Investment Awareness

### 🛡️ Comprehensive AI Guardrails
- **Input:** Prompt injection, jailbreak, sensitive data masking (OTP, PIN, CVV, Aadhaar), XSS prevention
- **Output:** Hallucination detection, unsafe advice prevention, credential leakage detection
- **RAG:** Document injection detection, relevance threshold, source validation
- **Rate Limiting:** Per-session minute/hour limits
- **Human-in-the-Loop:** Fraud escalation to 1930 / cybercrime.gov.in

### 📊 Admin Monitoring Dashboard
- LLM performance (latency, tokens, success rate)
- RAG retrieval analytics (relevance, groundedness)
- Agent execution traces
- Guardrail event monitoring
- Feedback / response quality metrics
- **Downloadable CSV reports**
- Date-range filtering

### 🔒 Security
- Environment variable-based secrets (never hardcoded)
- bcrypt password hashing for admin dashboard
- Input sanitization (HTML escape, length limits)
- Sensitive data redaction in logs
- Rate limiting per session

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- IBM WatsonX API credentials (optional – works in RAG-only mode without)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/finsaakhi.git
cd finsaakhi
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your IBM credentials:

```env
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_ibm_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_GRANITE_MODEL_ID=ibm/granite-3-3-8b-instruct
```

> **Note:** Without IBM credentials, the app runs in RAG-only mode, answering directly from the built-in knowledge base.

### 5. Run the application

```bash
# Main chat interface
streamlit run app.py

# Admin monitoring dashboard (separate terminal)
streamlit run dashboard.py --server.port 8502
```

Open your browser:
- **Chat App:** http://localhost:8501
- **Admin Dashboard:** http://localhost:8502 (default credentials: admin / admin123)

---

## 🗂️ Project Structure

```
finsaakhi/
├── app.py                          # Main Streamlit chat application
├── dashboard.py                    # Admin monitoring dashboard
├── config.py                       # Centralised configuration
├── database.py                     # SQLAlchemy models and DB init
├── llm_client.py                   # IBM Granite LLM client
├── auth.py                         # Dashboard authentication
│
├── agents/
│   ├── base_agent.py               # Base agent with RAG + LLM + guardrails
│   ├── supervisor_agent.py         # Query routing supervisor
│   └── specialized_agents.py      # 6 domain-specific agents
│
├── guardrails/
│   ├── input_guardrails.py         # Input validation, injection detection
│   └── output_guardrails.py        # Output safety, hallucination detection
│
├── middleware/
│   └── rate_limiter.py             # Per-session rate limiting
│
├── monitoring/
│   ├── agent_monitor.py            # Agent execution tracking
│   ├── rag_monitor.py              # RAG retrieval monitoring
│   ├── guardrail_monitor.py        # Guardrail event logging
│   ├── execution_tracer.py         # End-to-end request tracing
│   ├── dashboard_service.py        # Dashboard data queries
│   └── system_monitor.py           # System health checks
│
├── rag/
│   ├── rag_pipeline.py             # RAG retrieval pipeline
│   └── knowledge_base.py           # Trusted financial knowledge base
│
├── quizzes/
│   └── quiz_data.py                # Financial literacy quiz questions
│
├── pages/
│   └── 1_📚_Financial_Literacy.py  # Interactive learning modules + quizzes
│
├── tests/
│   ├── test_rag.py                 # RAG pipeline tests
│   ├── test_guardrails.py          # Guardrail tests
│   ├── test_rate_limiter.py        # Rate limiting tests
│   ├── test_quiz.py                # Quiz data tests
│   └── test_dashboard_service.py   # Dashboard service tests
│
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_rag.py -v
pytest tests/test_guardrails.py -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=term-missing -v
```

---

## 🔑 IBM WatsonX Setup

1. Create an IBM Cloud account at [cloud.ibm.com](https://cloud.ibm.com)
2. Create a WatsonX.ai project at [watsonx.ai](https://watsonx.ai)
3. Generate an API key at **IBM Cloud → IAM → API Keys**
4. Copy your Project ID from **WatsonX.ai → Projects → Your Project → Manage**
5. Add credentials to `.env`:

```env
IBM_API_KEY=<your-api-key>
IBM_PROJECT_ID=<your-project-id>
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_GRANITE_MODEL_ID=ibm/granite-3-3-8b-instruct
```

---

## 🔒 Security Best Practices

1. **Never commit `.env`** — it's in `.gitignore`
2. **Rotate secrets** regularly in production
3. **Set a proper admin password hash** for the dashboard:
   ```bash
   python -c "import bcrypt; print(bcrypt.hashpw(b'your_secure_password', bcrypt.gensalt(12)).decode())"
   ```
   Add the output to `.env` as `ADMIN_PASSWORD_HASH`
4. **Use PostgreSQL** for production instead of SQLite
5. **Enable HTTPS** in production deployment

---

## 📋 Knowledge Sources

All financial information is sourced from official Indian government and regulatory bodies:

| Source | Domain | Coverage |
|--------|--------|----------|
| Reserve Bank of India | rbi.org.in | Banking, loans, interest rates |
| NPCI | npci.org.in | UPI, digital payments |
| Indian Cyber Crime Portal | cybercrime.gov.in | Scam detection, fraud reporting |
| PM Jan Dhan Yojana | pmjdy.gov.in | Financial inclusion schemes |
| SEBI | sebi.gov.in | Investments, securities |
| IRDAI | irdai.gov.in | Insurance |
| Government of India | india.gov.in | General government schemes |

---

## 🚨 Emergency Helplines

| Service | Number |
|---------|--------|
| National Cyber Crime Helpline | **1930** |
| RBI Helpline | **14448** |
| SEBI Investor Helpline | **1800-266-7575** |
| IRDAI Helpline | **155255** |

---

## ⚠️ Disclaimer

FinSakhi provides **educational information only** and is **not a substitute for professional financial advice**. All financial decisions should be verified with official sources (RBI, NPCI, SEBI, IRDAI) and, where appropriate, a SEBI-registered financial advisor.

Interest rates, scheme details, and policy information are subject to change. Always verify current information at official government websites before making financial decisions.

---

## 📜 License

This project is developed for **IBM WatsonX Hackathon – Problem Statement #7: AI Agent for Digital Financial Literacy**.

---

*Made with ❤️ using IBM Granite | FinSakhi AI Financial Literacy Assistant*
