"""
pages/1_📚_Financial_Literacy.py – Interactive Financial Literacy Modules.
Full redesign: card grid, animated quiz, progress tracker, polished source display.
"""
from __future__ import annotations
import streamlit as st
from quizzes.quiz_data import QUIZZES, get_quiz
from rag.knowledge_base import KNOWLEDGE_BASE, SOURCE_REGISTRY, get_module_metadata

st.set_page_config(
    page_title="FinSakhi – Financial Literacy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, "Segoe UI", system-ui, sans-serif;
}
.block-container { padding-top: 1rem !important; }

/* ── Dark sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
    border-right: 1px solid #312e81;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.35) !important;
    border-color: #818cf8 !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.18) !important;
}
section[data-testid="stSidebar"] .stRadio > div > label {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px; padding: 6px 10px;
    margin-bottom: 4px; color: #cbd5e1 !important;
    font-size: 0.83rem; cursor: pointer;
    transition: all 0.15s;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(99,102,241,0.25) !important;
    border-color: #818cf8 !important;
}
section[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }

/* ── Page hero ── */
.lit-hero {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
    border-radius: 20px; padding: 2rem 2.5rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(79,70,229,0.3);
    position: relative; overflow: hidden;
}
.lit-hero::after {
    content: '';
    position: absolute; top: -50px; right: -50px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.lit-hero-title { font-size: 2rem; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; }
.lit-hero-sub   { font-size: 0.95rem; color: rgba(255,255,255,0.8); margin: 0.5rem 0 1rem; }
.lit-hero-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.lit-pill {
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.75rem; color: #fff; font-weight: 500;
}

/* ── Progress tracker ── */
.prog-bar-wrap {
    background: #e5e7eb; border-radius: 8px;
    height: 8px; margin: 8px 0 4px; overflow: hidden;
}
.prog-bar-fill {
    height: 100%; border-radius: 8px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    transition: width 0.5s ease;
}

/* ── Section header ── */
.section-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, #eff6ff, #f5f3ff);
    border: 1px solid #c7d2fe; border-radius: 8px;
    padding: 6px 14px; font-size: 0.82rem; font-weight: 600;
    color: #3730a3; margin-bottom: 1rem;
}

/* ── Content card ── */
.content-card {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 16px; padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
}
.content-card h3 { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-bottom: 0.8rem; }
.content-section-header {
    font-size: 0.88rem; font-weight: 700; color: #1a56db;
    text-transform: uppercase; letter-spacing: 0.5px;
    border-bottom: 2px solid #e0e7ff; padding-bottom: 4px;
    margin: 1rem 0 0.5rem;
}

/* ── Source citation row ── */
.src-row {
    display: flex; align-items: center; gap: 10px;
    background: #f8faff; border: 1px solid #e0e7ff;
    border-left: 3px solid #4f46e5;
    border-radius: 0 10px 10px 0;
    padding: 0.55rem 1rem; margin-top: 0.8rem;
    font-size: 0.78rem;
}
.src-row-name { font-weight: 700; color: #1e293b; }
.src-row-url  { color: #4f46e5; font-weight: 500; }
.src-row-date { color: #94a3b8; }

/* ── Tip / danger boxes ── */
.tip-card {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-left: 4px solid #22c55e;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem; margin: 0.4rem 0;
    font-size: 0.87rem; color: #14532d; line-height: 1.5;
}
.danger-card {
    background: #fef2f2; border: 1px solid #fecaca;
    border-left: 4px solid #ef4444;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem; margin: 0.4rem 0;
    font-size: 0.87rem; color: #7f1d1d; line-height: 1.5;
}

/* ── Source chips ── */
.chip-rbi  { display:inline-block;background:#fef2f2;color:#991b1b;border:1px solid #fecaca;border-radius:20px;padding:3px 10px;font-size:0.72rem;font-weight:600;margin:2px; }
.chip-npci { display:inline-block;background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe;border-radius:20px;padding:3px 10px;font-size:0.72rem;font-weight:600;margin:2px; }
.chip-sebi { display:inline-block;background:#f5f3ff;color:#5b21b6;border:1px solid #ddd6fe;border-radius:20px;padding:3px 10px;font-size:0.72rem;font-weight:600;margin:2px; }
.chip-irdai{ display:inline-block;background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;border-radius:20px;padding:3px 10px;font-size:0.72rem;font-weight:600;margin:2px; }
.chip-govt { display:inline-block;background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;border-radius:20px;padding:3px 10px;font-size:0.72rem;font-weight:600;margin:2px; }

/* ── Helpline grid ── */
.hl-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:0.8rem; }
.hl-card {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border-radius: 12px; padding: 0.9rem 1rem;
    text-align: center; color: #fff;
}
.hl-card-icon { font-size: 1.4rem; display:block; margin-bottom: 4px; }
.hl-card-label{ font-size: 0.72rem; color: rgba(255,255,255,0.7); }
.hl-card-num  { font-size: 1.3rem; font-weight: 800; color: #a5b4fc; display:block; margin-top: 2px; }

/* ── Quiz ── */
.quiz-hero {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 16px; padding: 1.5rem 2rem;
    color: #fff; margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(79,70,229,0.35);
}
.quiz-hero-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 4px; }
.quiz-hero-sub   { font-size: 0.88rem; opacity: 0.85; }
.quiz-counter {
    display: inline-flex; gap: 16px; margin-top: 0.8rem;
}
.quiz-counter-item { text-align: center; }
.quiz-counter-num { font-size: 1.6rem; font-weight: 800; color: #fff; }
.quiz-counter-lbl { font-size: 0.7rem; opacity: 0.75; }

.q-card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 14px; padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.q-card:hover { box-shadow: 0 4px 16px rgba(79,70,229,0.12); }
.q-num  { font-size: 0.72rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.q-text { font-size: 1rem; font-weight: 700; color: #1e293b; line-height: 1.4; }

/* ── Score ring animation ── */
.score-wrap {
    text-align: center; padding: 2rem 1rem;
    background: linear-gradient(135deg, #f0f4ff 0%, #fdf4ff 100%);
    border: 1px solid #c7d2fe; border-radius: 20px;
    margin-bottom: 1.5rem;
}
.score-ring {
    display: inline-block;
    width: 140px; height: 140px;
    border-radius: 50%;
    background: conic-gradient(var(--ring-color) var(--pct), #e5e7eb 0);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem; position: relative;
}
.score-ring-inner {
    width: 104px; height: 104px;
    background: #fff; border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.score-big { font-size: 2.2rem; font-weight: 800; color: #1e293b; line-height: 1; }
.score-pct { font-size: 0.8rem; color: #64748b; font-weight: 500; }
.score-grade { font-size: 1.3rem; font-weight: 700; color: #4f46e5; margin-bottom: 4px; }
.score-msg   { font-size: 0.9rem; color: #64748b; }

/* ── Answer review cards ── */
.rev-correct {
    background: #f0fdf4; border: 1px solid #86efac;
    border-left: 4px solid #22c55e;
    border-radius: 0 12px 12px 0; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.rev-wrong {
    background: #fef2f2; border: 1px solid #fca5a5;
    border-left: 4px solid #ef4444;
    border-radius: 0 12px 12px 0; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.rev-q    { font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.rev-ans  { font-size: 0.82rem; color: #475569; margin-bottom: 6px; }
.rev-exp  { font-size: 0.82rem; color: #374151; background: rgba(0,0,0,0.04); border-radius: 8px; padding: 6px 10px; }

/* ── Submit button ── */
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.75rem !important;
    box-shadow: 0 4px 16px rgba(79,70,229,0.35) !important;
    transition: all 0.2s !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    opacity: 0.92 !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.45) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
MODULE_META = get_module_metadata()

TIPS_DATA = {
    "upi_payments":     {"tips": ["Always verify recipient UPI ID before sending","Enable transaction SMS alerts in your app","Set a daily UPI transaction limit in settings"],"dangers": ["NEVER share your UPI PIN with anyone","Reject collect requests from unknown persons","Don't scan QR codes from strangers to 'receive' money"]},
    "fraud_detection":  {"tips": ["Save 1930 in your phone for instant fraud reporting","Always verify callers with official bank number","Check SEBI registration before any investment"],"dangers": ["No scheme can guarantee fixed high returns","Real police/CBI never demand money over phone","Never pay fees to claim lottery winnings"]},
    "safe_banking":     {"tips": ["Set up SMS/email alerts for all transactions","Review bank statements every month","Use virtual keyboard when available for net banking"],"dangers": ["Never use public WiFi for banking","Never save passwords on shared computers","Never accept help from strangers at ATM"]},
    "loans_interest":   {"tips": ["Compare at least 3 lenders before taking a loan","Read prepayment penalty clauses carefully","Use RBI EMI calculator at rbi.org.in"],"dangers": ["Don't take personal loan for stock market investing","Don't ignore credit card dues — 42% annual interest!","Don't borrow from unregistered lenders"]},
    "personal_budgeting":{"tips": ["Automate savings transfer on salary day (pay yourself first)","Track every expense for 30 days to find patterns","Review and adjust your budget every month"],"dangers": ["Don't wait to 'save what's left' — you'll save nothing","Don't ignore small daily expenses — they accumulate fast","Don't keep emergency fund in equity investments"]},
    "savings_emergency":{"tips": ["Build 3-6 months emergency fund before investing","Verify all interest rates directly at rbi.org.in or nsiindia.gov.in","Keep emergency fund in liquid savings or liquid MF"],"dangers": ["Don't invest emergency fund in equities","Don't fall for 'guaranteed 15%+ savings' schemes","Don't lock all savings in long-term instruments"]},
    "govt_schemes":     {"tips": ["PMJDY account opening is free — no charges ever","PMJJBY gives ₹2 lakh life cover for just ₹436/year","Enroll in APY before age 30 for lower monthly contributions"],"dangers": ["Beware of fake 'PMJDY benefit release' calls asking for OTP","Never pay middlemen/agents for free government scheme enrollment","Always verify schemes at official .gov.in websites only"]},
    "digital_security": {"tips": ["Use 12+ character passwords with uppercase, numbers, symbols","Enable biometric or 2FA on all banking apps","Keep phone OS and apps updated for security patches"],"dangers": ["Never share screen for banking 'verification'","Don't download banking apps from unofficial links","Don't use the same password for banking and other sites"]},
    "credit_scores":    {"tips": ["Check your free CIBIL report once a year at cibil.com","Set auto-debit for at least minimum credit card payment","Keep credit utilization below 30% of your total limit"],"dangers": ["Never pay only the minimum due — 42% annual interest trap","Don't apply for too many loans/cards in a short time","Don't close old credit cards unnecessarily"]},
    "investment_basics":{"tips": ["Verify SEBI registration at sebi.gov.in before investing","Start SIP with as little as ₹500/month and stay consistent","Check mutual fund ratings at amfiindia.com or mfcentral.com"],"dangers": ["No legitimate scheme guarantees high fixed returns","Don't invest based on WhatsApp/Telegram 'insider tips'","Don't invest borrowed money in equity markets"]},
    "insurance":        {"tips": ["Buy term insurance = 10-20× your annual income","Buy health insurance early — premiums rise with age","Verify IRDAI registration at irdai.gov.in before buying any policy"],"dangers": ["Don't treat insurance as your primary investment vehicle","Never hide pre-existing conditions — claim gets rejected","Never pay insurance premium in cash to agents"]},
}

SOURCE_CHIP_MAP = {
    "rbi.org.in":       "chip-rbi",
    "npci.org.in":      "chip-npci",
    "sebi.gov.in":      "chip-sebi",
    "irdai.gov.in":     "chip-irdai",
}


def get_module_docs(module_key: str, lang_code: str = "en"):
    docs = [d for d in KNOWLEDGE_BASE if d.get("module") == module_key and d.get("language") == lang_code]
    if not docs:
        docs = [d for d in KNOWLEDGE_BASE if d.get("module") == module_key and d.get("language") == "en"]
    return docs


def chip_class(domain: str) -> str:
    for k, v in SOURCE_CHIP_MAP.items():
        if k in domain:
            return v
    return "chip-govt"


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 0.8rem;display:flex;align-items:center;gap:10px;">
      <div style="font-size:1.8rem;">📚</div>
      <div>
        <div style="font-size:1.1rem;font-weight:800;color:#fff;">Financial Literacy</div>
        <div style="font-size:0.7rem;color:#94a3b8;">Learn · Quiz · Stay Safe</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    module_list   = list(MODULE_META.items())
    module_labels = [f"{v['icon']} {v['title']}" for _, v in module_list]
    module_keys   = [k for k, _ in module_list]

    st.markdown('<div style="font-size:0.72rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">📋 Modules</div>', unsafe_allow_html=True)
    selected_idx = st.radio(
        "mod", range(len(module_labels)),
        format_func=lambda i: module_labels[i],
        label_visibility="collapsed",
    )
    selected_module = module_keys[selected_idx]
    selected_meta   = MODULE_META[selected_module]

    st.divider()
    st.markdown('<div style="font-size:0.72rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">👁️ View Mode</div>', unsafe_allow_html=True)
    view_mode = st.radio("view", ["📖 Learn", "🧠 Quiz"], horizontal=True, label_visibility="collapsed")

    st.divider()
    st.markdown('<div style="font-size:0.72rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">🌐 Language</div>', unsafe_allow_html=True)
    language  = st.selectbox("lang", ["English", "हिन्दी (Hindi)", "తెలుగు (Telugu)"], label_visibility="collapsed")
    lang_map  = {"English": "en", "हिन्दी (Hindi)": "hi", "తెలుగు (Telugu)": "te"}
    lang      = lang_map[language]

    # Module progress
    completed_key = "quiz_completed"
    if completed_key not in st.session_state:
        st.session_state[completed_key] = set()
    done  = len(st.session_state[completed_key])
    total = len(module_keys)
    pct_done = int(done / total * 100) if total else 0
    st.divider()
    st.markdown(f'<div style="font-size:0.72rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">🏆 Quiz Progress</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.8rem;color:#a5b4fc;margin-bottom:4px;">{done}/{total} modules completed</div>'
        f'<div style="background:rgba(255,255,255,0.1);border-radius:4px;height:6px;">'
        f'<div style="background:#a5b4fc;border-radius:4px;height:6px;width:{pct_done}%;transition:width 0.4s;"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("🏠  Back to Chat", use_container_width=True):
        st.switch_page("app.py")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="lit-hero">
  <div style="font-size:2.5rem;margin-bottom:0.4rem;">{selected_meta['icon']}</div>
  <div class="lit-hero-title">{selected_meta['title']}</div>
  <div class="lit-hero-sub">{selected_meta['description']}</div>
  <div class="lit-hero-pills">
    <span class="lit-pill">📌 Source: {selected_meta['source']}</span>
    <span class="lit-pill">{'📖 Learn Mode' if '📖' in view_mode else '🧠 Quiz Mode'}</span>
    <span class="lit-pill">🌐 {language}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LEARN MODE
# ══════════════════════════════════════════════════════════════════════════════
if "📖" in view_mode:

    docs = get_module_docs(selected_module, lang)
    if not docs:
        st.info("ℹ️ Content for this language is not yet available. Showing English version.")
        docs = get_module_docs(selected_module, "en")

    # ── Source attribution row ──────────────────────────────────────────────────
    sources_seen = {d["source"] for d in docs}
    chips_html = "".join(
        f'<span class="{chip_class(s)}">📌 {SOURCE_REGISTRY.get(s, {}).get("name", s)}</span>'
        for s in sources_seen
    )
    st.markdown(f'<div style="margin-bottom:1rem;">{chips_html}</div>', unsafe_allow_html=True)

    # ── Content cards ───────────────────────────────────────────────────────────
    for doc in docs:
        content     = doc["content"]
        source_date = doc.get("source_date", "")
        si          = SOURCE_REGISTRY.get(doc["source"], {})

        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)

            # Parse and render content
            lines = content.split("\n")
            buffer = []
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if buffer:
                        st.markdown("\n".join(buffer))
                        buffer = []
                elif stripped.isupper() and 4 < len(stripped) < 80:
                    if buffer:
                        st.markdown("\n".join(buffer))
                        buffer = []
                    st.markdown(f'<div class="content-section-header">{stripped}</div>', unsafe_allow_html=True)
                else:
                    buffer.append(stripped)
            if buffer:
                st.markdown("\n".join(buffer))

            # Source citation
            date_txt = f" · Updated: {source_date}" if source_date else ""
            st.markdown(
                f'<div class="src-row">'
                f'<span>📌</span>'
                f'<span><span class="src-row-name">{si.get("name", doc["source"])}</span> &nbsp;'
                f'<a class="src-row-url" href="{si.get("url","#")}" target="_blank">{si.get("url","#")}</a>'
                f'<span class="src-row-date">{date_txt}</span></span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Best practices + Avoid section ─────────────────────────────────────────
    tips_data = TIPS_DATA.get(selected_module, {"tips": [], "dangers": []})

    st.markdown('<div class="section-tag">📋 Quick Reference Guide</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="font-size:1rem;font-weight:700;color:#166534;margin-bottom:8px;">✅ Best Practices</div>', unsafe_allow_html=True)
        for tip in tips_data.get("tips", []):
            st.markdown(f'<div class="tip-card">{tip}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="font-size:1rem;font-weight:700;color:#991b1b;margin-bottom:8px;">🚫 Common Mistakes</div>', unsafe_allow_html=True)
        for danger in tips_data.get("dangers", []):
            st.markdown(f'<div class="danger-card">{danger}</div>', unsafe_allow_html=True)

    # ── Emergency helplines ─────────────────────────────────────────────────────
    st.markdown('<br><div class="section-tag">📞 Emergency Helplines</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hl-grid">
      <div class="hl-card"><span class="hl-card-icon">🚨</span><span class="hl-card-label">Cyber Crime</span><span class="hl-card-num">1930</span></div>
      <div class="hl-card"><span class="hl-card-icon">🏦</span><span class="hl-card-label">RBI Helpline</span><span class="hl-card-num">14448</span></div>
      <div class="hl-card"><span class="hl-card-icon">📈</span><span class="hl-card-label">SEBI Investor</span><span class="hl-card-num">1800-266-7575</span></div>
      <div class="hl-card"><span class="hl-card-icon">🛡️</span><span class="hl-card-label">IRDAI</span><span class="hl-card-num">155255</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Call to action quiz ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    cta_c1, cta_c2 = st.columns([3, 1])
    with cta_c1:
        st.info(f"💡 Ready to test your knowledge? Switch to **🧠 Quiz Mode** from the sidebar!")


# ══════════════════════════════════════════════════════════════════════════════
# QUIZ MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    questions = get_quiz(selected_module)

    if not questions:
        st.warning(f"No quiz questions available for **{selected_meta['title']}** yet.")
        st.stop()

    state_key = f"quiz_{selected_module}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {"answers": {}, "submitted": False, "score": 0}
    quiz_st = st.session_state[state_key]

    # ── Quiz hero stats ─────────────────────────────────────────────────────────
    completed = st.session_state.get("quiz_completed", set())
    is_done   = selected_module in completed
    st.markdown(f"""
    <div class="quiz-hero">
      <div class="quiz-hero-title">🧠 Quiz: {selected_meta['title']}</div>
      <div class="quiz-hero-sub">Fact-based questions from official Indian financial sources</div>
      <div class="quiz-counter">
        <div class="quiz-counter-item"><div class="quiz-counter-num">{len(questions)}</div><div class="quiz-counter-lbl">Questions</div></div>
        <div class="quiz-counter-item"><div class="quiz-counter-num">{'✅' if is_done else '—'}</div><div class="quiz-counter-lbl">{'Completed' if is_done else 'Pending'}</div></div>
        <div class="quiz-counter-item"><div class="quiz-counter-num">{quiz_st['score'] if quiz_st['submitted'] else '?'}</div><div class="quiz-counter-lbl">Score</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RESULTS SCREEN ──────────────────────────────────────────────────────────
    if quiz_st["submitted"]:
        score = quiz_st["score"]
        total = len(questions)
        pct   = int(score / total * 100)

        if pct >= 80:
            ring_color, grade, grade_msg = "#22c55e", "Excellent! 🏆", "Outstanding performance!"
        elif pct >= 60:
            ring_color, grade, grade_msg = "#f59e0b", "Good! 👍", "You're on the right track."
        else:
            ring_color, grade, grade_msg = "#ef4444", "Keep Learning! 📚", "Review the module and try again."

        st.markdown(f"""
        <div class="score-wrap">
          <div style="display:inline-block;position:relative;width:140px;height:140px;margin:0 auto 1rem;">
            <svg width="140" height="140" viewBox="0 0 140 140" style="transform:rotate(-90deg)">
              <circle cx="70" cy="70" r="58" fill="none" stroke="#e5e7eb" stroke-width="12"/>
              <circle cx="70" cy="70" r="58" fill="none" stroke="{ring_color}" stroke-width="12"
                stroke-dasharray="{int(364 * pct / 100)} 364"
                stroke-linecap="round"/>
            </svg>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;">
              <div class="score-big">{score}/{total}</div>
              <div class="score-pct">{pct}%</div>
            </div>
          </div>
          <div class="score-grade">{grade}</div>
          <div class="score-msg">{grade_msg}</div>
        </div>
        """, unsafe_allow_html=True)

        # Progress bar
        st.markdown(f"""
        <div style="margin:-0.5rem 0 1.2rem;">
          <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#64748b;margin-bottom:4px;">
            <span>Score</span><span>{score}/{total} correct</span>
          </div>
          <div class="prog-bar-wrap">
            <div class="prog-bar-fill" style="width:{pct}%"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Mark module as completed
        st.session_state.get("quiz_completed", set()).add(selected_module)
        if "quiz_completed" not in st.session_state:
            st.session_state["quiz_completed"] = {selected_module}
        else:
            st.session_state["quiz_completed"].add(selected_module)

        # Answer review
        st.markdown('<div class="section-tag">📝 Answer Review</div>', unsafe_allow_html=True)
        for i, q in enumerate(questions):
            user_ans  = quiz_st["answers"].get(i, "")
            correct   = q["answer"]
            is_right  = user_ans == correct
            card_cls  = "rev-correct" if is_right else "rev-wrong"
            icon      = "✅" if is_right else "❌"

            # Find correct option text
            opt_map = {opt[0]: opt[3:] for opt in q["options"]}
            correct_text = opt_map.get(correct, correct)
            user_text    = opt_map.get(user_ans, user_ans or "Not answered")

            st.markdown(
                f'<div class="{card_cls}">'
                f'<div class="rev-q">{icon} Q{i+1}. {q["q"]}</div>'
                f'<div class="rev-ans">Your answer: <b>{user_ans or "—"}</b> — {user_text} &nbsp;|&nbsp; Correct: <b>{correct}</b> — {correct_text}</div>'
                f'<div class="rev-exp">💡 {q["explanation"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        col_r, col_n = st.columns(2)
        with col_r:
            if st.button("🔄  Retake Quiz", use_container_width=True):
                st.session_state[state_key] = {"answers": {}, "submitted": False, "score": 0}
                st.rerun()
        with col_n:
            next_modules = [k for k in module_keys if k != selected_module]
            if next_modules and st.button("➡️  Next Module", use_container_width=True):
                # navigate to next by re-setting radio state is not directly possible;
                # show a tip instead
                st.info("Select the next module from the sidebar to continue learning!")

    # ── QUESTION SCREEN ─────────────────────────────────────────────────────────
    else:
        st.markdown(
            f'<div style="font-size:0.85rem;color:#64748b;margin-bottom:1rem;">'
            f'📋 <b>{len(questions)} questions</b> — Select the best answer for each, then click Submit.'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.form(f"quiz_form_{selected_module}"):
            user_answers = {}
            for i, q in enumerate(questions):
                st.markdown(
                    f'<div class="q-card">'
                    f'<div class="q-num">Question {i+1} of {len(questions)}</div>'
                    f'<div class="q-text">{q["q"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                user_answers[i] = st.radio(
                    f"ans_{i}",
                    q["options"],
                    key=f"qopt_{selected_module}_{i}",
                    label_visibility="collapsed",
                )
                st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button("✅  Submit Answers", use_container_width=True)

        if submitted:
            score = 0
            clean = {}
            for i, q in enumerate(questions):
                opt = user_answers.get(i, "")
                letter = opt[0] if opt else ""
                clean[i] = letter
                if letter == q["answer"]:
                    score += 1
            st.session_state[state_key] = {"answers": clean, "submitted": True, "score": score}
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="margin-top:2rem;padding:1rem 1.5rem;background:#f8fafc;border-top:1px solid #e5e7eb;
border-radius:0 0 12px 12px;font-size:0.75rem;color:#64748b;display:flex;
justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <span>📚 FinSakhi Financial Literacy · Powered by IBM Granite</span>
  <span>Sources: RBI · NPCI · SEBI · IRDAI · Government of India · Cyber Crime Portal</span>
</div>
""", unsafe_allow_html=True)
