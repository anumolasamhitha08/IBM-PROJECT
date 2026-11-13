"""
agents/supervisor_agent.py – Supervisor Agent: routes queries, validates responses.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from agents.specialized_agents import (
    BudgetPlanningAgent,
    FinancialLiteracyAgent,
    GovernmentSchemesAgent,
    MultilingualAgent,
    ScamDetectionAgent,
    UPISafetyAgent,
)
from monitoring.agent_monitor import track_agent
from monitoring.execution_tracer import TraceContext

logger = logging.getLogger("finsaakhi.supervisor")

# ── Routing keywords ───────────────────────────────────────────────────────────
_ROUTING_RULES = [
    ("UPISafetyAgent",          re.compile(r"\bupi\b|unified\s+payment|gpay|phonepe|paytm|bhim|send\s+money", re.I)),
    ("ScamDetectionAgent",      re.compile(r"\bscam(?:med|ming)?\b|\bfraud\b|\bfake\b|\bphishing\b|\bcheat(?:ed|ing)?\b|\bstolen\b|cybercrime|report\s+fraud|being\s+(?:scammed|cheated|defrauded)", re.I)),
    ("BudgetPlanningAgent",     re.compile(r"\bbudget\b|\bexpense\b|\bsaving\b|\bspend\b|\b50.30.20\b|\bemi\b|monthly\s+plan", re.I)),
    ("GovernmentSchemesAgent",  re.compile(r"\bjandhan\b|\bpmjdy\b|\bpm\s+kisan\b|\bpmay\b|\bsubsidy\b|\bscheme\b|\bwelfare\b|\bration\b|\bsuraksha\b", re.I)),
]
_DEFAULT_AGENT = "FinancialLiteracyAgent"

_AGENT_REGISTRY = {
    "FinancialLiteracyAgent": FinancialLiteracyAgent,
    "UPISafetyAgent":         UPISafetyAgent,
    "ScamDetectionAgent":     ScamDetectionAgent,
    "BudgetPlanningAgent":    BudgetPlanningAgent,
    "GovernmentSchemesAgent": GovernmentSchemesAgent,
    "MultilingualAgent":      MultilingualAgent,
}


def _route(query: str, language: str) -> str:
    for agent_name, pattern in _ROUTING_RULES:
        if pattern.search(query):
            return agent_name
    # Non-English queries go through MultilingualAgent first
    if language != "en":
        return "MultilingualAgent"
    return _DEFAULT_AGENT


class SupervisorAgent:
    """
    Orchestrates the full request:
    Input validation → Agent routing → Specialized agent → Response validation
    """
    name = "SupervisorAgent"

    def process(
        self,
        validated_query: str,
        language: str = "en",
        request_id: str = None,
        trace: Optional[TraceContext] = None,
    ) -> Dict[str, Any]:
        # ── Route ──────────────────────────────────────────────────────────────
        target_name = _route(validated_query, language)
        AgentClass = _AGENT_REGISTRY[target_name]
        agent = AgentClass()

        if trace:
            trace.agent_sequence = ["SupervisorAgent", target_name]
            trace.add_step(f"SupervisorAgent:route → {target_name}", "ok")

        # ── Execute specialized agent ──────────────────────────────────────────
        with track_agent(target_name, language=language, request_category=target_name) as agent_ctx:
            result = agent.run(
                query=validated_query,
                language=language,
                request_id=request_id,
                trace=trace,
            )
            agent_ctx.llm_calls = (trace.llm_calls if trace else 0)
            agent_ctx.token_consumption = (trace.total_tokens if trace else 0)

        if trace:
            trace.add_step("SupervisorAgent:validate_response", "ok")

        # ── Supervisor validation ──────────────────────────────────────────────
        if not result.get("grounded") and not result.get("response"):
            result["response"] = _unsupported_message(language)
            result["warnings"] = result.get("warnings", []) + [
                "ℹ️ I could not find verified information. Please consult official sources."
            ]

        result["agent_used"] = target_name
        result["request_id"] = request_id
        return result


def _unsupported_message(lang: str) -> str:
    msgs = {
        "en": "I don't have verified information on this topic. Please visit rbi.org.in or npci.org.in for authoritative answers.",
        "hi": "मेरे पास इस विषय पर सत्यापित जानकारी नहीं है। कृपया rbi.org.in या npci.org.in पर जाएं।",
        "te": "ఈ అంశంపై నాకు ధృవీకరించిన సమాచారం లేదు. దయచేసి rbi.org.in లేదా npci.org.in సందర్శించండి.",
    }
    return msgs.get(lang, msgs["en"])
