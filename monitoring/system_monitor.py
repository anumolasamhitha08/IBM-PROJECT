"""
monitoring/system_monitor.py – System health checks (IBM Granite, DB, memory).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Dict, Any

import config
from monitoring.telemetry import record_system_event

logger = logging.getLogger("finsaakhi.system_monitor")


def check_ibm_granite() -> Dict[str, Any]:
    """Ping IBM WatsonX to verify connectivity. Returns status dict."""
    if not config.is_ibm_configured():
        record_system_event("ibm_granite", "health_check", "down", "IBM credentials not configured")
        return {"status": "down", "message": "IBM credentials not configured", "latency_ms": None}

    start = time.time()
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        creds = Credentials(url=config.IBM_WATSONX_URL, api_key=config.IBM_API_KEY)
        model = ModelInference(
            model_id=config.IBM_GRANITE_MODEL_ID,
            credentials=creds,
            project_id=config.IBM_PROJECT_ID,
        )
        # Minimal test generate
        model.generate_text("ping", params={"max_new_tokens": 1})
        latency = (time.time() - start) * 1000
        record_system_event("ibm_granite", "health_check", "ok", "Connected", latency)
        return {"status": "ok", "message": "Connected", "latency_ms": round(latency, 2)}
    except Exception as exc:
        latency = (time.time() - start) * 1000
        msg = str(exc)[:256]
        record_system_event("ibm_granite", "health_check", "down", msg, latency)
        return {"status": "down", "message": msg, "latency_ms": round(latency, 2)}


def check_database() -> Dict[str, Any]:
    from database import SessionLocal
    start = time.time()
    try:
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        latency = (time.time() - start) * 1000
        record_system_event("database", "health_check", "ok", "Connected", latency)
        return {"status": "ok", "latency_ms": round(latency, 2)}
    except Exception as exc:
        latency = (time.time() - start) * 1000
        record_system_event("database", "health_check", "down", str(exc)[:256], latency)
        return {"status": "down", "message": str(exc)[:256], "latency_ms": round(latency, 2)}


def check_vector_db() -> Dict[str, Any]:
    start = time.time()
    try:
        import chromadb
        client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        client.heartbeat()
        latency = (time.time() - start) * 1000
        return {"status": "ok", "latency_ms": round(latency, 2)}
    except Exception as exc:
        return {"status": "down", "message": str(exc)[:256]}


def get_system_resources() -> Dict[str, Any]:
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        return {
            "cpu_percent": round(cpu, 1),
            "memory_percent": round(mem.percent, 1),
            "memory_used_mb": round(mem.used / 1024 / 1024, 1),
            "memory_total_mb": round(mem.total / 1024 / 1024, 1),
        }
    except Exception:
        return {"cpu_percent": None, "memory_percent": None}


def full_health_check() -> Dict[str, Any]:
    return {
        "ibm_granite": check_ibm_granite(),
        "database": check_database(),
        "vector_db": check_vector_db(),
        "resources": get_system_resources(),
        "checked_at": datetime.utcnow().isoformat(),
    }
