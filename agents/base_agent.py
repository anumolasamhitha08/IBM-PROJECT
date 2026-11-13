"""
agents/base_agent.py – Base class for all FinSakhi agents with guardrails + monitoring.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import config
from guardrails.input_guardrails import InputValidationResult
from guardrails.output_guardrails import validate_output
from llm_client import generate_response
from monitoring.agent_monitor import AgentExecContext, track_agent
from monitoring.execution_tracer import TraceContext
from rag.rag_pipeline import format_context, retrieve

logger = logging.getLogger("finsaakhi.agents")


class BaseAgent(ABC):
    """All FinSakhi agents extend this."""

    name: str = "BaseAgent"
    role: str = ""
    allowed_categories: List[str] = []

    def __init__(self):
        self._step_count = 0

    @abstractmethod
    def _build_prompt(self, query: str, context: str, language: str) -> str:
        ...

    def run(
        self,
        query: str,
        language: str = "en",
        request_id: str = None,
        trace: Optional[TraceContext] = None,
    ) -> Dict[str, Any]:
        """
        Execute the agent: RAG retrieval → prompt build → LLM call → output validation.
        Returns response dict.
        """
        self._step_count += 1
        if self._step_count > config.MAX_AGENT_EXECUTION_STEPS:
            from monitoring.guardrail_monitor import log_agent_guardrail
            log_agent_guardrail("execution_limit_exceeded", request_id=request_id)
            return {"success": False, "response": "Execution limit exceeded.", "sources": []}

        # ── RAG retrieval ──────────────────────────────────────────────────────
        docs, rag_ctx = retrieve(query, language=language, request_id=request_id)
        context_str = format_context(docs)
        sources = [d["source"] for d in docs]

        if trace:
            trace.add_step(f"{self.name}:rag_retrieval", "ok", rag_ctx.retrieval_latency_ms)
            trace.tool_calls += 1

        # ── Build prompt ───────────────────────────────────────────────────────
        prompt = self._build_prompt(query, context_str, language)

        # ── LLM call ───────────────────────────────────────────────────────────
        llm_failed = False
        if not config.is_ibm_configured():
            response_text = self._fallback_response(query, docs, language)
            llm_ctx = None
        else:
            try:
                response_text, llm_ctx = generate_response(
                    prompt=prompt,
                    agent_name=self.name,
                    language=language,
                    request_category=self.name,
                )
                if trace and llm_ctx:
                    trace.llm_calls += 1
                    trace.total_tokens += llm_ctx.total_tokens
            except Exception as exc:
                logger.error("%s LLM call failed: %s", self.name, exc)
                # Fall back to RAG document content instead of a generic error
                response_text = self._fallback_response(query, docs, language)
                llm_ctx = None
                llm_failed = True

        # ── Output validation ──────────────────────────────────────────────────
        # Skip groundedness/uncertainty check for pure RAG fallback responses
        # to avoid a misleading "unable to verify" warning on good RAG content.
        out_result = validate_output(
            response_text,
            retrieved_docs=[d["content"] for d in docs] if not llm_failed else [],
            request_id=request_id,
            language=language,
        )

        if trace:
            trace.add_step(f"{self.name}:output_validation", "ok")
            if out_result.blocked or out_result.uncertainty_warning:
                trace.guardrails_triggered += 1

        return {
            "success": True,
            "response": out_result.safe_text,
            "sources": sources,
            # Suppress groundedness warning when serving direct RAG fallback
            "warnings": [w for w in out_result.warnings if not llm_failed or "verify" not in w.lower()],
            "grounded": rag_ctx.grounded,
            "docs_retrieved": len(docs),
            "uncertainty": out_result.uncertainty_warning and not llm_failed,
        }

    def _fallback_response(self, query: str, docs: List[Dict], language: str) -> str:
        """Used when IBM Granite is not configured."""
        if not docs:
            msgs = {
                "en": "IBM Granite is not connected. I cannot answer your question right now. Please check the configuration.",
                "hi": "IBM Granite कनेक्ट नहीं है। अभी आपके प्रश्न का उत्तर नहीं दे सकता। कृपया कॉन्फिगरेशन जांचें।",
                "te": "IBM Granite కనెక్ట్ కాలేదు. ఇప్పుడు మీ ప్రశ్నకు సమాధానం ఇవ్వలేను.",
            }
            return msgs.get(language, msgs["en"])
        # Return first retrieved document as fallback
        return docs[0]["content"] + f"\n\n*Source: {docs[0]['source']}*"

    def _error_response(self, language: str) -> str:
        msgs = {
            "en": "I encountered a temporary error. Please try again in a moment.",
            "hi": "एक अस्थायी त्रुटि हुई। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
            "te": "తాత్కాలిక లోపం ఏర్పడింది. దయచేసి కొంచెం సేపటికి మళ్ళీ ప్రయత్నించండి.",
        }
        return msgs.get(language, msgs["en"])
