"""
monitoring/execution_tracer.py – Full request execution trace recorder.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

from database import ExecutionTrace, SessionLocal
from monitoring.telemetry import safe_record

logger = logging.getLogger("finsaakhi.tracer")


class TraceContext:
    def __init__(self, language: str = "en"):
        self.trace_id = str(uuid.uuid4())
        self.language = language
        self.request_category: Optional[str] = None
        self.agent_sequence: List[str] = []
        self.total_duration_ms: float = 0.0
        self.llm_calls: int = 0
        self.tool_calls: int = 0
        self.total_tokens: int = 0
        self.success: bool = True
        self.error_category: Optional[str] = None
        self.guardrails_triggered: int = 0
        self.steps: List[Dict[str, Any]] = []
        self._start: float = 0.0

    def start(self):
        self._start = time.time()

    def add_step(self, step_name: str, status: str = "ok", duration_ms: float = 0.0):
        """Append a step – never include user prompt text."""
        self.steps.append({
            "step": step_name,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "ts": datetime.utcnow().isoformat(),
        })

    def finish(self, success: bool = True, error_category: str = None):
        self.total_duration_ms = (time.time() - self._start) * 1000
        self.success = success
        self.error_category = error_category


@safe_record
def save_trace(ctx: TraceContext) -> None:
    db = SessionLocal()
    try:
        record = ExecutionTrace(
            trace_id=ctx.trace_id,
            request_category=ctx.request_category,
            language=ctx.language,
            agent_sequence=json.dumps(ctx.agent_sequence),
            total_duration_ms=ctx.total_duration_ms,
            llm_calls=ctx.llm_calls,
            tool_calls=ctx.tool_calls,
            total_tokens=ctx.total_tokens,
            success=ctx.success,
            error_category=ctx.error_category,
            guardrails_triggered=ctx.guardrails_triggered,
            step_details=json.dumps(ctx.steps),
            timestamp=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


@contextmanager
def trace_request(language: str = "en", category: str = None) -> Generator[TraceContext, None, None]:
    ctx = TraceContext(language=language)
    ctx.request_category = category
    ctx.start()
    try:
        yield ctx
        if ctx.total_duration_ms == 0.0:
            ctx.finish(success=True)
    except Exception as exc:
        ctx.finish(success=False, error_category=type(exc).__name__)
        raise
    finally:
        save_trace(ctx)
