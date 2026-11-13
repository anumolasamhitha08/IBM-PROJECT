"""
monitoring/agent_monitor.py – Track every AI agent execution.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from database import AgentExecution, SessionLocal
from monitoring.telemetry import safe_record

logger = logging.getLogger("finsaakhi.agent_monitor")

KNOWN_AGENTS = [
    "FinancialLiteracyAgent",
    "UPISafetyAgent",
    "ScamDetectionAgent",
    "BudgetPlanningAgent",
    "GovernmentSchemesAgent",
    "MultilingualAgent",
    "SupervisorAgent",
]


class AgentExecContext:
    def __init__(self, agent_name: str, language: str = "en"):
        self.execution_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.language = language
        self.request_category: Optional[str] = None
        self.execution_time_ms: float = 0.0
        self.success: bool = True
        self.error_category: Optional[str] = None
        self.llm_calls: int = 0
        self.tool_invocations: int = 0
        self.token_consumption: int = 0
        self.retry_count: int = 0
        self._start: float = 0.0

    def start(self):
        self._start = time.time()

    def finish(self, success: bool = True, error_category: str = None):
        self.execution_time_ms = (time.time() - self._start) * 1000
        self.success = success
        self.error_category = error_category


@safe_record
def save_agent_execution(ctx: AgentExecContext) -> None:
    db = SessionLocal()
    try:
        record = AgentExecution(
            execution_id=ctx.execution_id,
            agent_name=ctx.agent_name,
            request_category=ctx.request_category,
            language=ctx.language,
            execution_time_ms=ctx.execution_time_ms,
            success=ctx.success,
            error_category=ctx.error_category,
            llm_calls=ctx.llm_calls,
            tool_invocations=ctx.tool_invocations,
            token_consumption=ctx.token_consumption,
            retry_count=ctx.retry_count,
            timestamp=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


@contextmanager
def track_agent(
    agent_name: str,
    language: str = "en",
    request_category: str = None,
) -> Generator[AgentExecContext, None, None]:
    """Context manager that times an agent execution and saves metrics."""
    ctx = AgentExecContext(agent_name=agent_name, language=language)
    ctx.request_category = request_category
    ctx.start()
    try:
        yield ctx
        if ctx.execution_time_ms == 0.0:
            ctx.finish(success=True)
    except Exception as exc:
        ctx.finish(success=False, error_category=type(exc).__name__)
        raise
    finally:
        save_agent_execution(ctx)
