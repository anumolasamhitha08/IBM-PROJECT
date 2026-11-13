"""
monitoring/telemetry.py – Core telemetry utilities shared across all monitors.
"""
from __future__ import annotations

import json
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from database import GuardrailEvent, SessionLocal, SystemEvent

logger = logging.getLogger("finsaakhi.telemetry")


def new_id() -> str:
    return str(uuid.uuid4())


def safe_record(fn):
    """Decorator: swallow any exception in monitoring code so it never crashes main app."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            logger.warning("Telemetry record error in %s: %s", fn.__name__, exc)
            return None
    return wrapper


@safe_record
def record_guardrail_event(
    guardrail_type: str,
    trigger_name: str,
    severity: str = "medium",
    action_taken: str = "blocked",
    request_id: Optional[str] = None,
    language: str = "en",
) -> None:
    db = SessionLocal()
    try:
        event = GuardrailEvent(
            event_id=new_id(),
            request_id=request_id,
            guardrail_type=guardrail_type,
            trigger_name=trigger_name,
            severity=severity,
            action_taken=action_taken,
            language=language,
            timestamp=datetime.utcnow(),
        )
        db.add(event)
        db.commit()
    finally:
        db.close()


@safe_record
def record_system_event(
    component: str,
    event_type: str,
    status: str,
    message: Optional[str] = None,
    latency_ms: Optional[float] = None,
) -> None:
    db = SessionLocal()
    try:
        event = SystemEvent(
            event_id=new_id(),
            component=component,
            event_type=event_type,
            status=status,
            message=message,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow(),
        )
        db.add(event)
        db.commit()
    finally:
        db.close()


def safe_json_dumps(obj: Any) -> str:
    try:
        return json.dumps(obj)
    except Exception:
        return "[]"
