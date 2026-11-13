"""
guardrails/output_guardrails.py – Validate LLM output before showing to user.
Prevents hallucinations, unsafe advice, credential leakage, and unsupported claims.
"""
from __future__ import annotations

import re
import logging
from typing import Tuple, Optional, List

from monitoring.guardrail_monitor import log_output_guardrail

logger = logging.getLogger("finsaakhi.guardrails.output")

# ── Unsafe financial advice patterns ──────────────────────────────────────────
_UNSAFE_ADVICE = [
    re.compile(r"\bguaranteed\s+return\b", re.I),
    re.compile(r"\b(?:100|1000)\s*%\s+(?:safe|profit|return)\b", re.I),
    re.compile(r"\binvest\s+all\s+your\s+(?:money|savings)\b", re.I),
    re.compile(r"\bnever\s+fail(?:s)?\b.*\binvest\b", re.I),
    re.compile(r"\bget\s+rich\s+quick\b", re.I),
    re.compile(r"\bdouble\s+your\s+money\b", re.I),
    re.compile(r"\bpyramid\s+(?:scheme|plan)\b", re.I),
    re.compile(r"\bponzi\b", re.I),
]

# ── Credential / system prompt leakage patterns ───────────────────────────────
_CREDENTIAL_LEAK = [
    re.compile(r"\bIBM_API_KEY\b", re.I),
    re.compile(r"\bapi[_\-]?key\s*[=:]\s*\S+", re.I),
    re.compile(r"\bsystem\s+prompt\b.*\b(?:is|reads|says)\b", re.I),
    re.compile(r"\bmy\s+instructions\s+(?:are|say|tell)\b", re.I),
]

# ── Hallucination indicators ───────────────────────────────────────────────────
_HALLUCINATION_INDICATORS = [
    re.compile(r"\bI\s+(?:am\s+)?(?:not\s+sure|uncertain)\s+but\b", re.I),
    re.compile(r"\bI\s+think\s+(?:it\s+)?(?:might|could|may)\s+be\b", re.I),
    re.compile(r"\bI\s+(?:believe|assume)\s+(?:that\s+)?the\s+(?:rate|amount|fee)\b", re.I),
]

# ── Sensitive data in output ───────────────────────────────────────────────────
_OUTPUT_SENSITIVE = [
    re.compile(r"\botp\s*[=:]\s*\d{4,8}\b", re.I),
    re.compile(r"\bpin\s*[=:]\s*\d{4,6}\b", re.I),
    re.compile(r"\bcvv\s*[=:]\s*\d{3,4}\b", re.I),
]


class OutputValidationResult:
    def __init__(self, text: str):
        self.original_text = text
        self.safe_text: str = text
        self.blocked: bool = False
        self.uncertainty_warning: bool = False
        self.unsafe_advice_detected: bool = False
        self.hallucination_risk: bool = False
        self.sources_present: bool = False
        self.warnings: List[str] = []


def validate_output(
    response_text: str,
    retrieved_docs: Optional[List[str]] = None,
    request_id: Optional[str] = None,
    language: str = "en",
) -> OutputValidationResult:
    result = OutputValidationResult(response_text)

    # 1. Credential / system leakage check
    for pattern in _CREDENTIAL_LEAK:
        if pattern.search(response_text):
            log_output_guardrail("credential_leakage_attempt", "critical", request_id, language)
            result.blocked = True
            result.safe_text = _get_blocked_message(language)
            return result

    # 2. Sensitive data in output
    for pattern in _OUTPUT_SENSITIVE:
        if pattern.search(response_text):
            log_output_guardrail("sensitive_data_in_output", "critical", request_id, language)
            result.blocked = True
            result.safe_text = _get_blocked_message(language)
            return result

    # 3. Unsafe financial advice
    for pattern in _UNSAFE_ADVICE:
        if pattern.search(response_text):
            log_output_guardrail("unsafe_financial_advice", "high", request_id, language)
            result.unsafe_advice_detected = True
            result.warnings.append(_unsafe_advice_warning(language))
            # Add disclaimer rather than block
            result.safe_text = response_text + "\n\n" + _financial_disclaimer(language)
            return result

    # 4. Hallucination indicators
    for pattern in _HALLUCINATION_INDICATORS:
        if pattern.search(response_text):
            result.hallucination_risk = True
            result.uncertainty_warning = True
            result.warnings.append(_uncertainty_warning(language))
            break

    # 5. Check groundedness (basic: does answer reference retrieved content?)
    if retrieved_docs:
        grounded = _check_groundedness(response_text, retrieved_docs)
        if not grounded:
            log_output_guardrail("ungrounded_response", "medium", request_id, language)
            result.uncertainty_warning = True
            result.warnings.append(_unverified_warning(language))

    # 6. Check for source citations
    result.sources_present = bool(
        re.search(r"(?:source|reference|according\s+to|from\s+rbi|from\s+npci|gov\.in)", response_text, re.I)
    )

    result.safe_text = response_text
    return result


def _check_groundedness(response: str, docs: List[str]) -> bool:
    """Simple keyword overlap check between response and retrieved docs."""
    if not docs:
        return False
    doc_words = set()
    for doc in docs:
        doc_words.update(doc.lower().split())
    response_words = set(response.lower().split())
    overlap = len(doc_words & response_words)
    return overlap >= 10  # Heuristic threshold


def _get_blocked_message(lang: str) -> str:
    msgs = {
        "en": "I cannot provide that information. Please ask a financial literacy question.",
        "hi": "मैं वह जानकारी प्रदान नहीं कर सकता। कृपया वित्तीय साक्षरता से संबंधित प्रश्न पूछें।",
        "te": "నేను ఆ సమాచారాన్ని అందించలేను. దయచేసి ఆర్థిక అక్షరాస్యత ప్రశ్న అడగండి.",
    }
    return msgs.get(lang, msgs["en"])


def _unsafe_advice_warning(lang: str) -> str:
    msgs = {
        "en": "⚠️ Please consult a SEBI-registered financial advisor before making investment decisions.",
        "hi": "⚠️ निवेश निर्णय लेने से पहले कृपया SEBI पंजीकृत वित्तीय सलाहकार से परामर्श करें।",
        "te": "⚠️ పెట్టుబడి నిర్ణయాలు తీసుకునే ముందు SEBI నమోదిత ఆర్థిక సలహాదారుని సంప్రదించండి.",
    }
    return msgs.get(lang, msgs["en"])


def _uncertainty_warning(lang: str) -> str:
    msgs = {
        "en": "ℹ️ This answer may not be fully verified. Please confirm with official sources.",
        "hi": "ℹ️ यह उत्तर पूरी तरह सत्यापित नहीं हो सकता। कृपया आधिकारिक स्रोतों से पुष्टि करें।",
        "te": "ℹ️ ఈ సమాధానం పూర్తిగా ధృవీకరించబడకపోవచ్చు. దయచేసి అధికారిక మూలాలతో నిర్ధారించండి.",
    }
    return msgs.get(lang, msgs["en"])


def _unverified_warning(lang: str) -> str:
    msgs = {
        "en": "ℹ️ Unable to fully verify this information from retrieved documents.",
        "hi": "ℹ️ पुनर्प्राप्त दस्तावेज़ों से इस जानकारी को पूरी तरह सत्यापित करने में असमर्थ।",
        "te": "ℹ️ తిరిగి పొందిన పత్రాల నుండి ఈ సమాచారాన్ని పూర్తిగా ధృవీకరించలేకపోయాను.",
    }
    return msgs.get(lang, msgs["en"])


def _financial_disclaimer(lang: str) -> str:
    msgs = {
        "en": "**Disclaimer:** This is for educational purposes only. Consult a certified financial advisor for personalized advice.",
        "hi": "**अस्वीकरण:** यह केवल शैक्षिक उद्देश्यों के लिए है। व्यक्तिगत सलाह के लिए प्रमाणित वित्तीय सलाहकार से परामर्श करें।",
        "te": "**నిరాకరణ:** ఇది విద్యా ప్రయోజనాల కోసం మాత్రమే. వ్యక్తిగతీకరించిన సలహా కోసం సర్టిఫైడ్ ఆర్థిక సలహాదారుని సంప్రదించండి.",
    }
    return msgs.get(lang, msgs["en"])
