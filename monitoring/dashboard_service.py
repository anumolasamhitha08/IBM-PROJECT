"""
monitoring/dashboard_service.py – Query layer for the admin dashboard.
All queries return DataFrames or dicts. Never returns raw user prompts.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy import func, text

import config
from database import (
    AgentExecution, ExecutionTrace, GuardrailEvent, LLMRequest,
    RAGEvent, ResponseFeedback, SessionLocal, SystemEvent,
)

logger = logging.getLogger("finsaakhi.dashboard")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _date_range(preset: str, custom_start: datetime = None, custom_end: datetime = None
                ) -> Tuple[datetime, datetime]:
    now = datetime.utcnow()
    if preset == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0), now
    elif preset == "last_7":
        return now - timedelta(days=7), now
    elif preset == "last_30":
        return now - timedelta(days=30), now
    elif preset == "custom" and custom_start and custom_end:
        return custom_start, custom_end
    return now - timedelta(days=30), now  # default


def _safe_rate(num: int, denom: int) -> Optional[float]:
    if denom == 0:
        return None
    return round((num / denom) * 100, 2)


# ─── LLM Analytics ────────────────────────────────────────────────────────────

def get_llm_summary(start: datetime, end: datetime) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rows = db.query(LLMRequest).filter(
            LLMRequest.timestamp >= start,
            LLMRequest.timestamp <= end,
        ).all()
        total = len(rows)
        success = sum(1 for r in rows if r.success)
        failed = total - success
        latencies = [r.latency_ms for r in rows if r.success and r.latency_ms > 0]
        tokens = [r.total_tokens for r in rows]
        return {
            "total_requests": total,
            "successful": success,
            "failed": failed,
            "success_rate": _safe_rate(success, total),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "min_latency_ms": round(min(latencies), 2) if latencies else None,
            "max_latency_ms": round(max(latencies), 2) if latencies else None,
            "total_tokens": sum(tokens),
            "avg_tokens": round(sum(tokens) / total, 1) if total else None,
            "model_id": config.IBM_GRANITE_MODEL_ID,
        }
    finally:
        db.close()


def get_llm_trend_df(start: datetime, end: datetime) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(LLMRequest).filter(
            LLMRequest.timestamp >= start,
            LLMRequest.timestamp <= end,
        ).order_by(LLMRequest.timestamp).all()
        if not rows:
            return pd.DataFrame(columns=["timestamp", "success", "latency_ms", "total_tokens"])
        data = [{"timestamp": r.timestamp, "success": r.success,
                 "latency_ms": r.latency_ms, "total_tokens": r.total_tokens} for r in rows]
        return pd.DataFrame(data)
    finally:
        db.close()


# ─── Agent Analytics ──────────────────────────────────────────────────────────

def get_agent_summary_df(start: datetime, end: datetime) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(AgentExecution).filter(
            AgentExecution.timestamp >= start,
            AgentExecution.timestamp <= end,
        ).all()
        if not rows:
            return pd.DataFrame()
        data = [{"agent_name": r.agent_name, "success": r.success,
                 "execution_time_ms": r.execution_time_ms,
                 "llm_calls": r.llm_calls, "token_consumption": r.token_consumption,
                 "tool_invocations": r.tool_invocations,
                 "retry_count": r.retry_count, "timestamp": r.timestamp} for r in rows]
        df = pd.DataFrame(data)
        summary = df.groupby("agent_name").agg(
            total_executions=("agent_name", "count"),
            successful=("success", "sum"),
            avg_time_ms=("execution_time_ms", "mean"),
            total_llm_calls=("llm_calls", "sum"),
            total_tokens=("token_consumption", "sum"),
            total_tools=("tool_invocations", "sum"),
            total_retries=("retry_count", "sum"),
            last_execution=("timestamp", "max"),
        ).reset_index()
        summary["failed"] = summary["total_executions"] - summary["successful"]
        summary["success_rate"] = summary.apply(
            lambda r: _safe_rate(int(r["successful"]), int(r["total_executions"])), axis=1
        )
        return summary
    finally:
        db.close()


def get_agent_executions_df(start: datetime, end: datetime, agent_name: str = None) -> pd.DataFrame:
    db = SessionLocal()
    try:
        q = db.query(AgentExecution).filter(
            AgentExecution.timestamp >= start,
            AgentExecution.timestamp <= end,
        )
        if agent_name:
            q = q.filter(AgentExecution.agent_name == agent_name)
        rows = q.order_by(AgentExecution.timestamp.desc()).limit(500).all()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "execution_id": r.execution_id, "agent_name": r.agent_name,
            "language": r.language, "execution_time_ms": r.execution_time_ms,
            "success": r.success, "llm_calls": r.llm_calls,
            "token_consumption": r.token_consumption, "timestamp": r.timestamp,
        } for r in rows])
    finally:
        db.close()


# ─── RAG Analytics ────────────────────────────────────────────────────────────

def get_rag_summary(start: datetime, end: datetime) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rows = db.query(RAGEvent).filter(
            RAGEvent.timestamp >= start, RAGEvent.timestamp <= end
        ).all()
        total = len(rows)
        success = sum(1 for r in rows if r.retrieval_success)
        grounded = sum(1 for r in rows if r.grounded)
        latencies = [r.retrieval_latency_ms for r in rows if r.retrieval_success]
        docs = [r.documents_retrieved for r in rows]
        relevances = [r.relevance_score for r in rows if r.relevance_score > 0]
        return {
            "total_retrievals": total,
            "successful": success,
            "failed": total - success,
            "success_rate": _safe_rate(success, total),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "avg_docs": round(sum(docs) / total, 1) if total else None,
            "avg_relevance": round(sum(relevances) / len(relevances), 3) if relevances else None,
            "grounded_rate": _safe_rate(grounded, total),
            "empty_retrievals": sum(1 for r in rows if r.empty_retrieval),
            "doc_validation_failures": sum(1 for r in rows if r.doc_validation_failed),
        }
    finally:
        db.close()


def get_rag_trend_df(start: datetime, end: datetime) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(RAGEvent).filter(
            RAGEvent.timestamp >= start, RAGEvent.timestamp <= end
        ).order_by(RAGEvent.timestamp).all()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "timestamp": r.timestamp, "success": r.retrieval_success,
            "docs": r.documents_retrieved, "relevance": r.relevance_score,
            "latency_ms": r.retrieval_latency_ms, "grounded": r.grounded,
        } for r in rows])
    finally:
        db.close()


# ─── Guardrail Analytics ──────────────────────────────────────────────────────

def get_guardrail_summary(start: datetime, end: datetime) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rows = db.query(GuardrailEvent).filter(
            GuardrailEvent.timestamp >= start, GuardrailEvent.timestamp <= end
        ).all()
        total = len(rows)
        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        for r in rows:
            by_type[r.guardrail_type] = by_type.get(r.guardrail_type, 0) + 1
            by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
        return {
            "total_triggers": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "critical": by_severity.get("critical", 0),
            "high": by_severity.get("high", 0),
        }
    finally:
        db.close()


def get_guardrail_df(start: datetime, end: datetime) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(GuardrailEvent).filter(
            GuardrailEvent.timestamp >= start, GuardrailEvent.timestamp <= end
        ).order_by(GuardrailEvent.timestamp.desc()).limit(500).all()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "timestamp": r.timestamp, "type": r.guardrail_type,
            "trigger": r.trigger_name, "severity": r.severity,
            "action": r.action_taken, "language": r.language,
        } for r in rows])
    finally:
        db.close()


# ─── Execution Traces ─────────────────────────────────────────────────────────

def get_traces_df(start: datetime, end: datetime) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(ExecutionTrace).filter(
            ExecutionTrace.timestamp >= start, ExecutionTrace.timestamp <= end
        ).order_by(ExecutionTrace.timestamp.desc()).limit(200).all()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([{
            "trace_id": r.trace_id[:12] + "...",
            "category": r.request_category,
            "language": r.language,
            "agents": r.agent_sequence,
            "duration_ms": r.total_duration_ms,
            "llm_calls": r.llm_calls,
            "tool_calls": r.tool_calls,
            "tokens": r.total_tokens,
            "success": r.success,
            "guardrails": r.guardrails_triggered,
            "timestamp": r.timestamp,
        } for r in rows])
    finally:
        db.close()


def get_trace_steps(trace_id_prefix: str) -> Optional[List[Dict]]:
    db = SessionLocal()
    try:
        row = db.query(ExecutionTrace).filter(
            ExecutionTrace.trace_id.like(trace_id_prefix + "%")
        ).first()
        if not row or not row.step_details:
            return None
        return json.loads(row.step_details)
    finally:
        db.close()


# ─── Response Quality / Feedback ──────────────────────────────────────────────

def get_feedback_summary(start: datetime, end: datetime) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rows = db.query(ResponseFeedback).filter(
            ResponseFeedback.timestamp >= start, ResponseFeedback.timestamp <= end
        ).all()
        total = len(rows)
        helpful = sum(1 for r in rows if r.rating == "helpful")
        not_helpful = sum(1 for r in rows if r.rating == "not_helpful")
        incorrect = sum(1 for r in rows if r.rating == "incorrect")
        relevances = [r.answer_relevance for r in rows if r.answer_relevance is not None]
        groundedness = [r.groundedness for r in rows if r.groundedness is not None]
        hallucinations = sum(1 for r in rows if r.hallucination_detected)
        return {
            "total_feedback": total,
            "helpful": helpful,
            "not_helpful": not_helpful,
            "incorrect": incorrect,
            "helpful_rate": _safe_rate(helpful, total),
            "avg_relevance": round(sum(relevances) / len(relevances), 3) if relevances else None,
            "avg_groundedness": round(sum(groundedness) / len(groundedness), 3) if groundedness else None,
            "hallucination_count": hallucinations,
        }
    finally:
        db.close()


def save_feedback(request_id: str, rating: str, language: str = "en") -> None:
    import uuid
    from database import ResponseFeedback
    db = SessionLocal()
    try:
        fb = ResponseFeedback(
            feedback_id=str(uuid.uuid4()),
            request_id=request_id,
            rating=rating,
            language=language,
            timestamp=datetime.utcnow(),
        )
        db.add(fb)
        db.commit()
    except Exception as exc:
        logger.warning("Failed to save feedback: %s", exc)
        db.rollback()
    finally:
        db.close()


# ─── Overview KPIs ────────────────────────────────────────────────────────────

def get_overview_kpis(start: datetime, end: datetime) -> Dict[str, Any]:
    llm = get_llm_summary(start, end)
    rag = get_rag_summary(start, end)
    guardrail = get_guardrail_summary(start, end)
    db = SessionLocal()
    try:
        agent_rows = db.query(AgentExecution).filter(
            AgentExecution.timestamp >= start, AgentExecution.timestamp <= end
        ).all()
        total_agents = len(agent_rows)
        success_agents = sum(1 for r in agent_rows if r.success)
    finally:
        db.close()
    return {
        "llm_total": llm["total_requests"],
        "llm_success": llm["successful"],
        "llm_failed": llm["failed"],
        "llm_success_rate": llm["success_rate"],
        "avg_latency_ms": llm["avg_latency_ms"],
        "total_tokens": llm["total_tokens"],
        "agent_executions": total_agents,
        "agent_success_rate": _safe_rate(success_agents, total_agents),
        "rag_success_rate": rag["success_rate"],
        "guardrail_triggers": guardrail["total_triggers"],
    }
