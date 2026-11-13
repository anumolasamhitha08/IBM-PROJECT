"""
monitoring/rag_monitor.py – Track every RAG retrieval event.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from database import RAGEvent, SessionLocal
from monitoring.telemetry import safe_record

logger = logging.getLogger("finsaakhi.rag_monitor")


class RAGContext:
    def __init__(self, request_id: str = None, language: str = "en"):
        self.event_id = str(uuid.uuid4())
        self.request_id = request_id or str(uuid.uuid4())
        self.language = language
        self.retrieval_success: bool = True
        self.documents_retrieved: int = 0
        self.relevance_score: float = 0.0
        self.retrieval_latency_ms: float = 0.0
        self.sources_cited: int = 0
        self.grounded: bool = False
        self.unsupported: bool = False
        self.empty_retrieval: bool = False
        self.doc_validation_failed: bool = False
        self._start: float = 0.0

    def start(self):
        self._start = time.time()

    def finish(self, success: bool = True):
        self.retrieval_latency_ms = (time.time() - self._start) * 1000
        self.retrieval_success = success
        if self.documents_retrieved == 0:
            self.empty_retrieval = True


@safe_record
def save_rag_event(ctx: RAGContext) -> None:
    db = SessionLocal()
    try:
        record = RAGEvent(
            event_id=ctx.event_id,
            request_id=ctx.request_id,
            retrieval_success=ctx.retrieval_success,
            documents_retrieved=ctx.documents_retrieved,
            relevance_score=ctx.relevance_score,
            retrieval_latency_ms=ctx.retrieval_latency_ms,
            sources_cited=ctx.sources_cited,
            grounded=ctx.grounded,
            unsupported=ctx.unsupported,
            empty_retrieval=ctx.empty_retrieval,
            doc_validation_failed=ctx.doc_validation_failed,
            language=ctx.language,
            timestamp=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


@contextmanager
def track_rag(
    request_id: str = None,
    language: str = "en",
) -> Generator[RAGContext, None, None]:
    ctx = RAGContext(request_id=request_id, language=language)
    ctx.start()
    try:
        yield ctx
        if ctx.retrieval_latency_ms == 0.0:
            ctx.finish(success=True)
    except Exception as exc:
        ctx.finish(success=False)
        raise
    finally:
        save_rag_event(ctx)
