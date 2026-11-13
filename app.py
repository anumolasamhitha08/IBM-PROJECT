"""
app.py – FinSakhi AI Financial Literacy Chatbot (main Streamlit user interface).
Run: streamlit run app.py
"""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime

import streamlit as st

# ── Bootstrap ──────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
import config
from database import init_db

init_db()

logging.basicConfig(
    level=config.get_log_level(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("finsaakhi.app")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSakhi – AI Financial Literacy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, "Segoe UI", system-ui, sans-serif;
}
.block-container { padding-top: 1rem !important; }

/* ── Sidebar reskin ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
    border-right: 1px solid #312e81;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 { color: #ffffff !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.35) !important;
    border-color: #818cf8 !important;
    transform: translateX(2px);
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.18) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stMetric { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
    color: #a5b4fc !important; font-size: 1.6rem !important; font-weight: 800 !important;
}
section[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; font-size: 0.75rem !important; }

/* ── Hero banner ── */
.hero-wrap {
    background: linear-gradient(135deg, #1a56db 0%, #4f46e5 40%, #7c3aed 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem 1.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(79,70,229,0.35);
}
.hero-wrap::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.hero-wrap::after {
    content: '';
    position: absolute; bottom: -80px; left: 40%;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.hero-title {
    font-size: 2.2rem; font-weight: 800; color: #fff;
    letter-spacing: -0.5px; margin: 0; line-height: 1.2;
}
.hero-subtitle {
    font-size: 1rem; color: rgba(255,255,255,0.88);
    margin: 0.4rem 0 1.2rem; font-weight: 400;
}
.hero-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.8rem; }
.hero-pill {
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.78rem; color: #fff; font-weight: 500;
}
.hero-stats { display: flex; gap: 2rem; margin-top: 1rem; }
.hero-stat-num { font-size: 1.5rem; font-weight: 800; color: #fff; line-height: 1; }
.hero-stat-lbl { font-size: 0.72rem; color: rgba(255,255,255,0.75); margin-top: 1px; }

/* ── IBM Badge ── */
.ibm-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #161616; color: #fff;
    border: 1px solid #393939;
    padding: 5px 12px; border-radius: 8px;
    font-size: 0.73rem; font-weight: 600; letter-spacing: 0.3px;
}
.ibm-pill-warn { background: #7f1d1d; border-color: #991b1b; }

/* ── Quick-topic chips ── */
.topic-grid { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.5rem 0 1rem; }
.topic-chip {
    background: #f0f4ff; border: 1px solid #c7d2fe;
    border-radius: 20px; padding: 6px 14px;
    font-size: 0.8rem; color: #3730a3; font-weight: 500;
    cursor: pointer; transition: all 0.15s;
    text-decoration: none; display: inline-block;
}
.topic-chip:hover { background: #e0e7ff; border-color: #6366f1; color: #312e81; }

/* ── Chat bubbles ── */
.chat-row-user { display: flex; justify-content: flex-end; margin: 0.6rem 0; }
.chat-row-bot  { display: flex; justify-content: flex-start; margin: 0.6rem 0; gap: 10px; align-items: flex-start; }
.chat-avatar {
    width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; color: #fff; font-weight: 700;
    box-shadow: 0 2px 8px rgba(79,70,229,0.4);
}
.bubble-user {
    background: linear-gradient(135deg, #1a56db, #4f46e5);
    color: #fff;
    padding: 0.75rem 1.15rem;
    border-radius: 18px 4px 18px 18px;
    max-width: 75%; word-wrap: break-word;
    font-size: 0.92rem; line-height: 1.55;
    box-shadow: 0 2px 10px rgba(26,86,219,0.3);
}
.bubble-bot {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 0.85rem 1.15rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 80%; word-wrap: break-word;
    font-size: 0.92rem; line-height: 1.6; color: #1f2328;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.bubble-bot strong { color: #1a56db; }

/* ── Welcome card ── */
.welcome-card {
    background: linear-gradient(135deg, #f0f4ff 0%, #fdf4ff 100%);
    border: 1px solid #c7d2fe;
    border-radius: 16px; padding: 1.4rem 1.6rem;
    margin: 0.5rem 0 1rem;
    display: flex; gap: 1rem; align-items: flex-start;
}
.welcome-icon { font-size: 2.5rem; flex-shrink: 0; }
.welcome-text { font-size: 0.92rem; color: #374151; line-height: 1.6; }
.welcome-text b { color: #1a56db; }

/* ── Typing indicator ── */
.typing-indicator {
    display: flex; gap: 5px; align-items: center;
    padding: 0.7rem 1rem;
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 4px 18px 18px 18px;
    width: fit-content;
}
.typing-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #6366f1;
    animation: typing-bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
}

/* ── Source citation card ── */
.src-card {
    background: #fafbff; border: 1px solid #dde3f5;
    border-left: 3px solid #4f46e5;
    border-radius: 0 10px 10px 0;
    padding: 0.6rem 1rem; margin: 4px 0;
    font-size: 0.79rem;
}
.src-card-name { font-weight: 700; color: #1e293b; margin-bottom: 2px; }
.src-card-url  { color: #4f46e5; font-weight: 500; }
.src-card-date { color: #64748b; font-size: 0.72rem; }
.src-card-cat  { color: #94a3b8; font-size: 0.7rem; }

/* ── Feedback row ── */
.fb-row { display: flex; gap: 8px; align-items: center; margin-top: 6px; }
.fb-caption { font-size: 0.75rem; color: #64748b; margin-top: 3px; }

/* ── Warning/info banners ── */
.chat-warn {
    background: #fffbeb; border: 1px solid #fbbf24; border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0; padding: 0.55rem 0.9rem;
    margin: 4px 0; font-size: 0.82rem; color: #92400e;
}

/* ── Safety alert strip ── */
.safety-strip {
    background: linear-gradient(90deg, #fef2f2 0%, #fff7ed 50%, #f0fdf4 100%);
    border: 1px solid #fecaca; border-radius: 14px;
    padding: 1rem 1.4rem; margin-bottom: 1.2rem;
}
.safety-strip-title { font-weight: 700; color: #1f2328; margin-bottom: 0.7rem; font-size: 0.95rem; }
.alert-item {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 0.6rem 0.8rem; border-radius: 10px;
    margin-bottom: 0.4rem; font-size: 0.83rem; line-height: 1.5;
}
.alert-red   { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
.alert-green { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
.alert-blue  { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; }

/* ── Helpline bar ── */
.helpline-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 0.8rem; }
.helpline-badge {
    background: #0f172a; color: #fff; border-radius: 10px;
    padding: 0.55rem 1rem; font-size: 0.8rem; line-height: 1.4;
    flex: 1; min-width: 120px; text-align: center;
}
.helpline-badge .hl-num { font-size: 1.25rem; font-weight: 800; color: #a5b4fc; display: block; }

/* ── Security notice in sidebar ── */
.sec-notice {
    background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3);
    border-radius: 10px; padding: 0.7rem 0.9rem; font-size: 0.78rem;
    color: #86efac !important; line-height: 1.5;
}

/* ── Rate limit bar ── */
.rl-bar-wrap { margin: 4px 0 8px; }
.rl-bar-bg { background: rgba(255,255,255,0.1); border-radius: 4px; height: 5px; }
.rl-bar-fill { background: #a5b4fc; border-radius: 4px; height: 5px; transition: width 0.3s; }

/* ── Module tiles in sidebar ── */
.mod-tile {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 8px 12px; margin-bottom: 5px;
    cursor: pointer; transition: all 0.2s;
    display: flex; align-items: center; gap: 8px;
    font-size: 0.82rem; color: #cbd5e1 !important;
}
.mod-tile:hover { background: rgba(99,102,241,0.2); border-color: #818cf8; }

/* ── Footer ── */
.footer-bar {
    margin-top: 2rem; padding: 1rem 1.5rem;
    background: #f8fafc; border-top: 1px solid #e5e7eb;
    border-radius: 0 0 12px 12px;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 8px; font-size: 0.75rem; color: #64748b;
}
.footer-link { color: #4f46e5; text-decoration: none; font-weight: 500; }

/* ── Stray Streamlit padding fix ── */
div[data-testid="stVerticalBlock"] > div { gap: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
LANGUAGES = {"🇬🇧 English": "en", "🇮🇳 हिंदी": "hi", "🔵 తెలుగు": "te"}

SUGGESTED_QUESTIONS = {
    "en": [
        "How do I send money via UPI safely?",
        "How to detect if I'm being scammed?",
        "What is PM Jan Dhan Yojana?",
        "How do I create a monthly budget?",
        "What is a good CIBIL credit score?",
        "How do I start SIP in mutual funds?",
    ],
    "hi": [
        "UPI से पैसे कैसे भेजें?",
        "क्या मैं धोखाधड़ी का शिकार हो रहा हूं?",
        "PM Jan Dhan Yojana क्या है?",
        "मासिक बजट कैसे बनाएं?",
    ],
    "te": [
        "UPI ద్వారా డబ్బు ఎలా పంపాలి?",
        "నేను మోసానికి గురవుతున్నానా?",
        "PM జన్ ధన్ యోజన అంటే ఏమిటి?",
        "నెలవారీ బడ్జెట్ ఎలా తయారు చేయాలి?",
    ],
}

TOPICS = {
    "en": ["💳 UPI Payments", "🚨 Scam Safety", "🏦 Banking", "📊 Budget", "🏛️ Govt Schemes", "📈 Investing"],
    "hi": ["💳 UPI भुगतान", "🚨 घोटाला पहचान", "🏦 बैंकिंग", "📊 बजट"],
    "te": ["💳 UPI చెల్లింపులు", "🚨 మోసం గుర్తింపు", "🏦 బ్యాంకింగ్"],
}

# ── Session init ───────────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "language": "en",
    "total_queries": 0,
    "session_id": str(uuid.uuid4()),
    "show_sources_for": set(),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo + name
    st.markdown("""
    <div style="padding:0.5rem 0 0.8rem; display:flex; align-items:center; gap:10px;">
      <div style="font-size:2rem;">💰</div>
      <div>
        <div style="font-size:1.25rem; font-weight:800; color:#fff; letter-spacing:-0.3px;">FinSakhi</div>
        <div style="font-size:0.72rem; color:#94a3b8;">AI Financial Literacy</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # IBM status pill
    ibm_ok = config.is_ibm_configured()
    if ibm_ok:
        st.markdown('<div class="ibm-pill">🟢 IBM Granite Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ibm-pill ibm-pill-warn">🔴 IBM Granite — RAG Mode</div>', unsafe_allow_html=True)
        st.caption("Add IBM credentials to `.env` to enable full LLM responses.")

    st.divider()

    # Language
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">🌐 Language</div>', unsafe_allow_html=True)
    st.markdown("""
<style>
div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)
    lang_label = st.selectbox("lang", list(LANGUAGES.keys()), label_visibility="collapsed")
    st.session_state.language = LANGUAGES[lang_label]

    st.divider()

    # Navigation
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">🗺️ Navigation</div>', unsafe_allow_html=True)
    if st.button("📚  Financial Literacy Modules", use_container_width=True):
        st.switch_page("pages/1_📚_Financial_Literacy.py")

    st.divider()

    # Suggested questions
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">💡 Quick Ask</div>', unsafe_allow_html=True)
    lang = st.session_state.language
    for q in SUGGESTED_QUESTIONS.get(lang, SUGGESTED_QUESTIONS["en"]):
        if st.button(q, key=f"sq_{hash(q)}", use_container_width=True):
            st.session_state["prefill_question"] = q
            st.rerun()

    st.divider()

    # Security notice
    st.markdown("""
    <div class="sec-notice">
    🔒 <b style="color:#86efac">Security Notice</b><br>
    Never share <b>UPI PIN, OTP, CVV</b> or banking passwords — not even with this assistant.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # Session stats
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">📊 Session</div>', unsafe_allow_html=True)
    st.metric("Queries", st.session_state.total_queries, label_visibility="visible")

    from middleware.rate_limiter import get_rate_limit_status
    rl = get_rate_limit_status(st.session_state.session_id)
    used = rl["requests_in_window"]
    mx   = rl["window_max"]
    pct  = int(used / mx * 100) if mx else 0
    st.markdown(
        f'<div class="rl-bar-wrap">'
        f'<div style="font-size:0.72rem;color:#94a3b8;margin-bottom:3px;">Rate limit: {mx-used}/{mx} left</div>'
        f'<div class="rl-bar-bg"><div class="rl-bar-fill" style="width:{pct}%"></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Admin Dashboard → `streamlit run dashboard.py`")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

# ── Hero banner ────────────────────────────────────────────────────────────────
ibm_ok = config.is_ibm_configured()
queries_today = st.session_state.total_queries
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-title">💰 FinSakhi</div>
  <div class="hero-subtitle">Your trusted AI guide to digital financial literacy — powered by IBM Granite</div>
  <div class="hero-pills">
    <span class="hero-pill">🇮🇳 India-focused</span>
    <span class="hero-pill">🛡️ Scam Protection</span>
    <span class="hero-pill">📱 UPI &amp; Payments</span>
    <span class="hero-pill">🌐 EN / हिं / తె</span>
    <span class="hero-pill">✅ Verified Sources</span>
  </div>
  <div class="hero-stats">
    <div><div class="hero-stat-num">6</div><div class="hero-stat-lbl">Trusted Sources</div></div>
    <div><div class="hero-stat-num">10+</div><div class="hero-stat-lbl">Learning Modules</div></div>
    <div><div class="hero-stat-num">35+</div><div class="hero-stat-lbl">Quiz Questions</div></div>
    <div><div class="hero-stat-num">{'🟢 Live' if ibm_ok else '🟡 RAG'}</div><div class="hero-stat-lbl">IBM Granite</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Topic quick-fire chips ─────────────────────────────────────────────────────
lang = st.session_state.language
topic_list = TOPICS.get(lang, TOPICS["en"])
chips_html = "".join(f'<span class="topic-chip">{t}</span>' for t in topic_list)
st.markdown(f'<div class="topic-grid">{chips_html}</div>', unsafe_allow_html=True)

# ── Safety alert strip ─────────────────────────────────────────────────────────
with st.expander("⚠️  Financial Safety — Alerts, Tips & Emergency Helplines", expanded=False):
    st.markdown("""
    <div class="safety-strip">
      <div class="safety-strip-title">⚠️ Stay Alert — Common Financial Threats</div>
      <div class="alert-item alert-red">
        🚨 <div><b>OTP / UPI PIN Scam:</b> Banks &amp; NPCI NEVER call asking for OTP, PIN, or passwords. Hang up immediately.</div>
      </div>
      <div class="alert-item alert-red">
        🚨 <div><b>Digital Arrest Scam:</b> Fake CBI / police threatening arrest over phone. Real agencies never work this way.</div>
      </div>
      <div class="alert-item alert-green">
        ✅ <div><b>UPI Safety Rule:</b> Enter your UPI PIN <b>only to SEND money</b>. You NEVER need a PIN to receive money.</div>
      </div>
      <div class="alert-item alert-blue">
        📈 <div><b>Investment Scams:</b> "Guaranteed 30% returns" is always a scam. Verify any advisor at <a href="https://sebi.gov.in/" target="_blank" style="color:#1e40af">sebi.gov.in</a>.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-weight:700;font-size:0.9rem;margin-bottom:8px;">📞 Emergency Helplines</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="helpline-bar">
      <div class="helpline-badge">🚨 Cyber Crime<span class="hl-num">1930</span></div>
      <div class="helpline-badge">🏦 RBI Helpline<span class="hl-num">14448</span></div>
      <div class="helpline-badge">📈 SEBI<span class="hl-num">1800-266-7575</span></div>
      <div class="helpline-badge">🛡️ IRDAI<span class="hl-num">155255</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:10px;font-size:0.78rem;color:#64748b;">
    Report cybercrime online:
    <a href="https://cybercrime.gov.in/" target="_blank" style="color:#4f46e5;font-weight:600;">cybercrime.gov.in</a>
    &nbsp;|&nbsp; RBI Ombudsman:
    <a href="https://bankingombudsman.rbi.org.in/" target="_blank" style="color:#4f46e5;font-weight:600;">bankingombudsman.rbi.org.in</a>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
chat_container = st.container()
with chat_container:

    # ── Welcome card (empty state) ──────────────────────────────────────────────
    if not st.session_state.messages:
        welcome_text = {
            "en": "👋 Hello! I'm <b>FinSakhi</b>, your AI guide to financial literacy in India.<br>Ask me about <b>UPI</b>, <b>budgeting</b>, <b>scam detection</b>, <b>loans</b>, <b>government schemes</b>, or <b>investment basics</b>.<br><br>I answer <i>only from verified official sources</i> — RBI, NPCI, SEBI, IRDAI and Government of India.",
            "hi": "👋 नमस्ते! मैं <b>FinSakhi</b> हूं, भारत में वित्तीय साक्षरता के लिए आपका AI गाइड।<br><b>UPI</b>, <b>बजट</b>, <b>धोखाधड़ी पहचान</b>, <b>ऋण</b>, <b>सरकारी योजनाओं</b> के बारे में पूछें।<br><br>मैं केवल सत्यापित आधिकारिक स्रोतों — RBI, NPCI, SEBI, IRDAI से उत्तर देता हूं।",
            "te": "👋 నమస్కారం! నేను <b>FinSakhi</b>, భారతదేశంలో ఆర్థిక అక్షరాస్యత కోసం మీ AI గైడ్.<br><b>UPI</b>, <b>బడ్జెట్</b>, <b>మోసం గుర్తింపు</b>, <b>రుణాలు</b>, <b>ప్రభుత్వ పథకాల</b> గురించి అడగండి.",
        }[lang]
        st.markdown(f"""
        <div class="welcome-card">
          <div class="welcome-icon">🤖</div>
          <div class="welcome-text">{welcome_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # Starter question buttons
        st.markdown('<div style="font-size:0.8rem;color:#64748b;margin:4px 0 8px;font-weight:500;">Try asking:</div>', unsafe_allow_html=True)
        q_cols = st.columns(2)
        for idx, q in enumerate(SUGGESTED_QUESTIONS.get(lang, SUGGESTED_QUESTIONS["en"])[:4]):
            with q_cols[idx % 2]:
                if st.button(f"💬 {q}", key=f"welcome_q_{idx}", use_container_width=True):
                    st.session_state["prefill_question"] = q
                    st.rerun()

    # ── Render messages ─────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(
                f'<div class="chat-row-user"><div class="bubble-user">{content}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            # Bot bubble with avatar
            st.markdown(
                f'<div class="chat-row-bot">'
                f'<div class="chat-avatar">FS</div>'
                f'<div class="bubble-bot">{content}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # ── Source citation cards ──────────────────────────────────────────
            sources      = msg.get("sources", [])
            source_dates = msg.get("source_dates", {})
            req_id       = msg.get("request_id", "")

            if sources:
                from rag.rag_pipeline import get_source_info
                unique_sources = list(dict.fromkeys(sources))

                col_btn, _ = st.columns([2, 5])
                with col_btn:
                    label = f"📌 {len(unique_sources)} Source{'s' if len(unique_sources) > 1 else ''}"
                    if st.button(label, key=f"src_toggle_{req_id}", help="Show / hide source citations"):
                        ss = st.session_state.show_sources_for
                        ss.discard(req_id) if req_id in ss else ss.add(req_id)

                if req_id in st.session_state.show_sources_for:
                    for src in unique_sources:
                        si  = get_source_info(src)
                        dt  = source_dates.get(src, "")
                        dt_html  = f'<span class="src-card-date"> · Updated {dt}</span>' if dt else ""
                        st.markdown(
                            f'<div class="src-card">'
                            f'<div class="src-card-name">📌 {si.get("name", src)}</div>'
                            f'<a class="src-card-url" href="{si.get("url","#")}" target="_blank">{si.get("url","#")}</a>'
                            f'{dt_html}<br>'
                            f'<span class="src-card-cat">{si.get("category","")}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            # ── Warnings ──────────────────────────────────────────────────────
            for w in msg.get("warnings", []):
                st.markdown(f'<div class="chat-warn">{w}</div>', unsafe_allow_html=True)

            # ── Feedback buttons ───────────────────────────────────────────────
            if req_id:
                fb_key = f"fb_{req_id}"
                if fb_key not in st.session_state:
                    st.session_state[fb_key] = None

                f1, f2, f3, _ = st.columns([1, 1, 1.5, 5])
                with f1:
                    if st.button("👍", key=f"helpful_{req_id}", help="Helpful"):
                        from monitoring.dashboard_service import save_feedback
                        save_feedback(req_id, "helpful", lang)
                        st.session_state[fb_key] = "helpful"
                with f2:
                    if st.button("👎", key=f"nothelpful_{req_id}", help="Not helpful"):
                        from monitoring.dashboard_service import save_feedback
                        save_feedback(req_id, "not_helpful", lang)
                        st.session_state[fb_key] = "not_helpful"
                with f3:
                    if st.button("⚠️ Incorrect", key=f"report_{req_id}", help="Report incorrect info"):
                        from monitoring.dashboard_service import save_feedback
                        save_feedback(req_id, "incorrect", lang)
                        st.session_state[fb_key] = "incorrect"

                fb = st.session_state[fb_key]
                if fb == "helpful":
                    st.markdown('<div class="fb-caption">✅ Thank you for your feedback!</div>', unsafe_allow_html=True)
                elif fb == "not_helpful":
                    st.markdown('<div class="fb-caption">📝 Feedback noted — we\'ll improve.</div>', unsafe_allow_html=True)
                elif fb == "incorrect":
                    st.markdown('<div class="fb-caption">⚠️ Reported. Please verify with official sources like rbi.org.in.</div>', unsafe_allow_html=True)


# ── Chat input ─────────────────────────────────────────────────────────────────
prefill     = st.session_state.pop("prefill_question", "")
user_input  = st.chat_input("Ask anything about UPI, scams, loans, budget, schemes… | पूछें… | అడగండి…")
if prefill:
    user_input = prefill


# ══════════════════════════════════════════════════════════════════════════════
# QUERY PROCESSOR
# ══════════════════════════════════════════════════════════════════════════════
def process_query(query: str) -> None:
    import uuid as _uuid
    from guardrails.input_guardrails import get_rejection_message, validate_input
    from monitoring.execution_tracer import trace_request
    from agents.supervisor_agent import SupervisorAgent
    from middleware.rate_limiter import check_rate_limit

    language   = st.session_state.language
    request_id = str(_uuid.uuid4())
    session_id = st.session_state.session_id

    # Rate limit
    rl = check_rate_limit(session_id)
    if not rl.allowed:
        st.warning(f"⏳ {rl.reason}")
        return

    st.session_state.total_queries += 1

    # Input guardrails
    validation = validate_input(query, request_id=request_id)
    if not validation.is_valid:
        msg = get_rejection_message(validation.rejection_reason, language)
        st.session_state.messages.append({
            "role": "assistant", "content": msg,
            "sources": [], "warnings": [], "request_id": request_id,
        })
        return

    for w in validation.warnings:
        st.info(w)

    sanitized    = validation.masked_input
    effective_lang = language if language != "en" else validation.detected_language

    # Full pipeline
    with trace_request(language=effective_lang, category="user_query") as trace:
        trace.add_step("input_guardrails", "ok")
        supervisor = SupervisorAgent()
        with st.spinner("🔍 Searching verified sources…"):
            result = supervisor.process(
                validated_query=sanitized,
                language=effective_lang,
                request_id=request_id,
                trace=trace,
            )
        trace.add_step("complete", "ok")

    response = result.get("response", "")
    sources  = result.get("sources", [])
    warnings = result.get("warnings", [])

    if not response:
        response = {
            "en": "I don't have verified information on this topic. Please visit rbi.org.in or npci.org.in.",
            "hi": "मेरे पास इस विषय पर सत्यापित जानकारी नहीं है। कृपया rbi.org.in पर जाएं।",
            "te": "ఈ అంశంపై నాకు ధృవీకరించిన సమాచారం లేదు. దయచేసి rbi.org.in సందర్శించండి.",
        }.get(effective_lang, "I don't have verified information on this topic.")

    # Collect source dates
    source_dates: dict = {}
    try:
        import importlib
        rp = importlib.import_module("rag.rag_pipeline")
        docs, _ = rp.retrieve(sanitized, effective_lang)
        for doc in docs:
            s, d = doc.get("source", ""), doc.get("source_date", "")
            if s and d:
                source_dates[s] = d
    except Exception:
        pass

    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": list(dict.fromkeys(sources)),
        "source_dates": source_dates,
        "warnings": warnings,
        "request_id": request_id,
    })


if user_input:
    process_query(user_input.strip())
    st.rerun()


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
  <span>💰 FinSakhi AI · Powered by IBM Granite · For educational purposes only</span>
  <span>
    🚨 Cyber Crime Helpline: <b>1930</b> &nbsp;|&nbsp;
    <a class="footer-link" href="https://cybercrime.gov.in/" target="_blank">cybercrime.gov.in</a> &nbsp;|&nbsp;
    <a class="footer-link" href="https://www.rbi.org.in/" target="_blank">rbi.org.in</a>
  </span>
</div>
""", unsafe_allow_html=True)
