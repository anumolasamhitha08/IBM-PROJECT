"""
monitoring/llm_monitor.py – Track every IBM Granite API call.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, Optional

from database import LLMRequest, SessionLocal
from monitoring.telemetry import safe_record

logger = logging.getLogger("finsaakhi.llm_monitor")


class LLMCallContext:
    """Context object populated during an LLM call, then saved."""

    def __init__(self, model_id: str, agent_name: str = "", language: str = "en"):
        self.request_id = str(uuid.uuid4())
        self.model_id = model_id
        self.agent_name = agent_name
        self.language = language
        self.request_category: Optional[str] = None
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
        self.latency_ms: float = 0.0
        self.success: bool = True
        self.error_type: Optional[str] = None
        self.error_message: Optional[str] = None
        self.retry_count: int = 0
        self._start: float = 0.0

    def start(self):
        self._start = time.time()

    def finish(self, success: bool = True, error_type: str = None, error_message: str = None):
        self.latency_ms = (time.time() - self._start) * 1000
        self.success = success
        self.error_type = error_type
        self.error_message = error_message

    def set_tokens(self, prompt: int = 0, completion: int = 0, total: int = 0):
        self.prompt_tokens = prompt
        self.completion_tokens = completion
        self.total_tokens = total or (prompt + completion)


@safe_record
def save_llm_call(ctx: LLMCallContext) -> None:
    db = SessionLocal()
    try:
        record = LLMRequest(
            request_id=ctx.request_id,
            model_id=ctx.model_id,
            prompt_tokens=ctx.prompt_tokens,
            completion_tokens=ctx.completion_tokens,
            total_tokens=ctx.total_tokens,
            latency_ms=ctx.latency_ms,
            success=ctx.success,
            error_type=ctx.error_type,
            error_message=ctx.error_message[:512] if ctx.error_message else None,
            retry_count=ctx.retry_count,
            agent_name=ctx.agent_name,
            request_category=ctx.request_category,
            language=ctx.language,
            timestamp=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


@contextmanager
def track_llm_call(
    model_id: str,
    agent_name: str = "",
    language: str = "en",
    request_category: str = None,
) -> Generator[LLMCallContext, None, None]:
    """Context manager that times an LLM call and saves metrics automatically."""
    ctx = LLMCallContext(model_id=model_id, agent_name=agent_name, language=language)
    ctx.request_category = request_category
    ctx.start()
    try:
        yield ctx
        if ctx.latency_ms == 0.0:
            ctx.finish(success=True)
    except Exception as exc:
        ctx.finish(success=False, error_type=type(exc).__name__, error_message=str(exc))
        raise
    finally:
        save_llm_call(ctx)
