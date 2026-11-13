"""
database.py – SQLAlchemy models and DB initialisation for FinSakhi AI monitoring.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, Index, Integer,
    String, Text, create_engine, event
)
from sqlalchemy.orm import declarative_base, sessionmaker

import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=False,
)

# Enable WAL mode for SQLite concurrency
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    if "sqlite" in config.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── LLM Requests ─────────────────────────────────────────────────────────────
class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(128), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    error_type = Column(String(128), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    agent_name = Column(String(64), nullable=True)
    request_category = Column(String(64), nullable=True)
    language = Column(String(8), default="en")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_llm_requests_timestamp", "timestamp"),
        Index("ix_llm_requests_success", "success"),
        Index("ix_llm_requests_agent", "agent_name"),
    )


# ─── Agent Executions ─────────────────────────────────────────────────────────
class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    agent_name = Column(String(64), nullable=False)
    request_category = Column(String(64), nullable=True)
    language = Column(String(8), default="en")
    execution_time_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    error_category = Column(String(64), nullable=True)
    llm_calls = Column(Integer, default=0)
    tool_invocations = Column(Integer, default=0)
    token_consumption = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_agent_executions_timestamp", "timestamp"),
        Index("ix_agent_executions_agent", "agent_name"),
        Index("ix_agent_executions_success", "success"),
    )


# ─── RAG Events ───────────────────────────────────────────────────────────────
class RAGEvent(Base):
    __tablename__ = "rag_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=True)
    retrieval_success = Column(Boolean, default=True)
    documents_retrieved = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    retrieval_latency_ms = Column(Float, default=0.0)
    sources_cited = Column(Integer, default=0)
    grounded = Column(Boolean, default=False)
    unsupported = Column(Boolean, default=False)
    empty_retrieval = Column(Boolean, default=False)
    doc_validation_failed = Column(Boolean, default=False)
    language = Column(String(8), default="en")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_rag_events_timestamp", "timestamp"),
        Index("ix_rag_events_success", "retrieval_success"),
    )


# ─── Guardrail Events ─────────────────────────────────────────────────────────
class GuardrailEvent(Base):
    __tablename__ = "guardrail_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=True)
    guardrail_type = Column(String(64), nullable=False)   # input, output, rag, agent, tool, privacy
    trigger_name = Column(String(128), nullable=False)
    severity = Column(String(16), default="medium")       # low, medium, high, critical
    action_taken = Column(String(64), default="blocked")  # blocked, warned, masked, escalated
    language = Column(String(8), default="en")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_guardrail_events_timestamp", "timestamp"),
        Index("ix_guardrail_events_type", "guardrail_type"),
        Index("ix_guardrail_events_severity", "severity"),
    )


# ─── Execution Traces ─────────────────────────────────────────────────────────
class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    request_category = Column(String(64), nullable=True)
    language = Column(String(8), default="en")
    agent_sequence = Column(Text, nullable=True)           # JSON list of agent names
    total_duration_ms = Column(Float, default=0.0)
    llm_calls = Column(Integer, default=0)
    tool_calls = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_category = Column(String(64), nullable=True)
    guardrails_triggered = Column(Integer, default=0)
    step_details = Column(Text, nullable=True)             # JSON – no user prompt
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_execution_traces_timestamp", "timestamp"),
        Index("ix_execution_traces_success", "success"),
    )


# ─── Response Feedback ────────────────────────────────────────────────────────
class ResponseFeedback(Base):
    __tablename__ = "response_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=True)
    rating = Column(String(32), nullable=False)            # helpful, not_helpful, incorrect
    answer_relevance = Column(Float, nullable=True)
    groundedness = Column(Float, nullable=True)
    faithfulness = Column(Float, nullable=True)
    language_correctness = Column(Float, nullable=True)
    hallucination_detected = Column(Boolean, default=False)
    language = Column(String(8), default="en")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_response_feedback_timestamp", "timestamp"),
    )


# ─── System Events ────────────────────────────────────────────────────────────
class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    component = Column(String(64), nullable=False)         # ibm_granite, rag, db, app
    event_type = Column(String(64), nullable=False)        # health_check, error, warning, info
    status = Column(String(32), nullable=False)            # ok, degraded, down
    message = Column(Text, nullable=True)
    latency_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_system_events_timestamp", "timestamp"),
        Index("ix_system_events_component", "component"),
    )


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency-injection style DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
