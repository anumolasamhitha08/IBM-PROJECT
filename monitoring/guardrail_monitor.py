"""
monitoring/guardrail_monitor.py – Guardrail event tracking helpers.
"""
from __future__ import annotations

from monitoring.telemetry import record_guardrail_event


def log_input_guardrail(trigger: str, severity: str = "medium", request_id: str = None, language: str = "en"):
    record_guardrail_event("input", trigger, severity, "blocked", request_id, language)


def log_output_guardrail(trigger: str, severity: str = "medium", request_id: str = None, language: str = "en"):
    record_guardrail_event("output", trigger, severity, "blocked", request_id, language)


def log_rag_guardrail(trigger: str, severity: str = "medium", request_id: str = None, language: str = "en"):
    record_guardrail_event("rag", trigger, severity, "blocked", request_id, language)


def log_agent_guardrail(trigger: str, severity: str = "high", request_id: str = None, language: str = "en"):
    record_guardrail_event("agent", trigger, severity, "blocked", request_id, language)


def log_tool_guardrail(trigger: str, severity: str = "high", request_id: str = None, language: str = "en"):
    record_guardrail_event("tool", trigger, severity, "blocked", request_id, language)


def log_privacy_guardrail(trigger: str, severity: str = "critical", request_id: str = None, language: str = "en"):
    record_guardrail_event("privacy", trigger, severity, "masked", request_id, language)
