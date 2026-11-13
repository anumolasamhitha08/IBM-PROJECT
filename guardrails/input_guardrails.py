"""
guardrails/input_guardrails.py – Validate and sanitize user inputs.
Covers: prompt injection, jailbreak, sensitive data, language support.
"""
from __future__ import annotations

import html
import re
import logging
from typing import Tuple, Optional

import config
from monitoring.guardrail_monitor import log_input_guardrail, log_privacy_guardrail

logger = logging.getLogger("finsaakhi.guardrails.input")

# ── Sensitive data patterns (never store or log matched values) ────────────────
_SENSITIVE_PATTERNS = {
    "otp":       re.compile(r"\b(?:otp|one[\s-]?time[\s-]?password)\s*[:\-]?\s*\d{4,8}\b", re.I),
    "upi_pin":   re.compile(r"\b(?:upi[\s-]?pin|mpin)\s*[:\-]?\s*\d{4,6}\b", re.I),
    "cvv":       re.compile(r"\b(?:cvv|cvc|cvv2)\s*[:\-]?\s*\d{3,4}\b", re.I),
    "password":  re.compile(r"\b(?:password|passwd|pwd)\s*[:\-]?\s*\S{4,}\b", re.I),
    "card_no":   re.compile(r"\b(?:\d[ -]?){15,16}\b"),
    "bank_acc":  re.compile(r"\b\d{9,18}\b"),
    "ifsc":      re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
    "aadhaar":   re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "pan":       re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
}

# ── Prompt injection / jailbreak patterns ─────────────────────────────────────
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(?:previous|above|prior)\s+instruction", re.I),
    re.compile(r"disregard\s+(?:your|all)\s+(?:instructions|guidelines|rules)", re.I),
    re.compile(r"you\s+are\s+now\s+(?:a|an)\s+(?!FinSakhi)", re.I),
    re.compile(r"pretend\s+(you\s+are|to\s+be)", re.I),
    re.compile(r"act\s+as\s+(?:a|an|if)\s+(?!financial|literacy)", re.I),
    re.compile(r"DAN\s+mode", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"prompt\s+injection", re.I),
    re.compile(r"reveal\s+(?:your\s+)?(?:system\s+prompt|instructions|api\s+key|secret)", re.I),
    re.compile(r"<\s*script[\s>]", re.I),
    re.compile(r"javascript\s*:", re.I),
    re.compile(r"\bSELECT\b.*\bFROM\b", re.I),  # SQL injection
]

# ── Off-topic / malicious request patterns ────────────────────────────────────
_OFFTOPIC_PATTERNS = [
    re.compile(r"\bhack(?:ing)?\b", re.I),
    re.compile(r"\bexploit\b", re.I),
    re.compile(r"\bmalware\b", re.I),
    re.compile(r"\bweapon\b", re.I),
    re.compile(r"\bdrug\b", re.I),
    re.compile(r"\bterror(?:ist|ism)?\b", re.I),
]

# ── Supported language codes ───────────────────────────────────────────────────
SUPPORTED_LANGS = set(config.SUPPORTED_LANGUAGES)

MAX_INPUT_LENGTH = 2000


class InputValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.blocked: bool = False
        self.masked_input: str = ""
        self.rejection_reason: Optional[str] = None
        self.detected_language: str = "en"
        self.sensitive_fields: list = []
        self.warnings: list = []


def detect_language(text: str) -> str:
    """Lightweight language detection without external calls."""
    try:
        from langdetect import detect
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGS else "en"
    except Exception:
        return "en"


def mask_sensitive(text: str) -> Tuple[str, list]:
    """Replace sensitive values with placeholders. Returns (masked_text, fields_found)."""
    found = []
    masked = text
    for field, pattern in _SENSITIVE_PATTERNS.items():
        if pattern.search(masked):
            found.append(field)
            masked = pattern.sub(f"[{field.upper()}_REDACTED]", masked)
    return masked, found


def validate_input(user_text: str, request_id: str = None) -> InputValidationResult:
    result = InputValidationResult()

    # 1. Basic sanitization
    sanitized = html.escape(user_text.strip())

    # 2. Length check
    if len(sanitized) > MAX_INPUT_LENGTH:
        sanitized = sanitized[:MAX_INPUT_LENGTH]
        result.warnings.append("Input truncated to maximum length.")

    # 3. Empty check
    if not sanitized:
        result.is_valid = False
        result.blocked = True
        result.rejection_reason = "empty_input"
        return result

    # 4. Sensitive data detection
    masked, fields = mask_sensitive(sanitized)
    if fields:
        for field in fields:
            log_privacy_guardrail(f"sensitive_{field}_in_input", request_id=request_id)
        result.sensitive_fields = fields
        result.warnings.append(
            "⚠️ For your security, please never share OTPs, PINs, passwords, or card numbers."
        )
        sanitized = masked

    # 5. Prompt injection / jailbreak
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(sanitized):
            log_input_guardrail("prompt_injection_attempt", "critical", request_id=request_id)
            result.is_valid = False
            result.blocked = True
            result.rejection_reason = "prompt_injection"
            return result

    # 6. Off-topic / malicious
    for pattern in _OFFTOPIC_PATTERNS:
        if pattern.search(sanitized):
            log_input_guardrail("off_topic_malicious_request", "high", request_id=request_id)
            result.is_valid = False
            result.blocked = True
            result.rejection_reason = "off_topic_malicious"
            return result

    # 7. Language detection
    result.detected_language = detect_language(sanitized)

    result.masked_input = sanitized
    return result


REJECTION_MESSAGES = {
    "empty_input": {
        "en": "Please enter your question.",
        "hi": "कृपया अपना प्रश्न दर्ज करें।",
        "te": "దయచేసి మీ ప్రశ్న నమోదు చేయండి.",
    },
    "prompt_injection": {
        "en": "I cannot process that request. Please ask a financial literacy question.",
        "hi": "मैं उस अनुरोध को संसाधित नहीं कर सकता। कृपया वित्तीय साक्षरता से संबंधित प्रश्न पूछें।",
        "te": "నేను ఆ అభ్యర్థనను ప్రాసెస్ చేయలేను. దయచేసి ఆర్థిక అక్షరాస్యత ప్రశ్న అడగండి.",
    },
    "off_topic_malicious": {
        "en": "I can only assist with financial literacy topics such as UPI, budgeting, and savings.",
        "hi": "मैं केवल वित्तीय साक्षरता विषयों जैसे UPI, बजट और बचत में सहायता कर सकता हूं।",
        "te": "నేను UPI, బడ్జెట్ మరియు పొదుపు వంటి ఆర్థిక అక్షరాస్యత అంశాలలో మాత్రమే సహాయం చేయగలను.",
    },
}


def get_rejection_message(reason: str, language: str = "en") -> str:
    msgs = REJECTION_MESSAGES.get(reason, {})
    return msgs.get(language, msgs.get("en", "I cannot process that request."))
