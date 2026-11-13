"""
config.py – Centralised configuration loader for FinSakhi AI.
Reads from .env file and provides typed settings.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env", override=False)

# ── IBM Granite / WatsonX ─────────────────────────────────────────────────────
IBM_API_KEY: str = os.getenv("IBM_API_KEY", "")
IBM_WATSONX_URL: str = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "")
IBM_GRANITE_MODEL_ID: str = os.getenv("IBM_GRANITE_MODEL_ID", "ibm/granite-3-3-8b-instruct")

# ── IBM Watson Discovery ──────────────────────────────────────────────────────
IBM_DISCOVERY_API_KEY: str = os.getenv("IBM_DISCOVERY_API_KEY", "")
IBM_DISCOVERY_URL: str = os.getenv("IBM_DISCOVERY_URL", "")
IBM_DISCOVERY_PROJECT_ID: str = os.getenv("IBM_DISCOVERY_PROJECT_ID", "")
IBM_DISCOVERY_VERSION: str = os.getenv("IBM_DISCOVERY_VERSION", "2023-03-31")

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///finsaakhi.db")

# ── Vector DB ─────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# ── Admin Auth ────────────────────────────────────────────────────────────────
ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH: str = os.getenv("ADMIN_PASSWORD_HASH", "")
ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "change_me_in_production")

# ── App Settings ──────────────────────────────────────────────────────────────
APP_NAME: str = os.getenv("APP_NAME", "FinSakhi")
APP_ENV: str = os.getenv("APP_ENV", "development")
APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "change_me")
SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

# ── Rate Limits ───────────────────────────────────────────────────────────────
MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))
MAX_TOKENS_PER_REQUEST: int = int(os.getenv("MAX_TOKENS_PER_REQUEST", "4096"))
MAX_AGENT_EXECUTION_STEPS: int = int(os.getenv("MAX_AGENT_EXECUTION_STEPS", "10"))
AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))
LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
TOOL_TIMEOUT_SECONDS: int = int(os.getenv("TOOL_TIMEOUT_SECONDS", "15"))
# Rate limiter specific settings
RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_PER_HOUR: int = int(os.getenv("RATE_LIMIT_MAX_PER_HOUR", "60"))

# ── RAG Settings ──────────────────────────────────────────────────────────────
RAG_MAX_DOCS: int = int(os.getenv("RAG_MAX_DOCS", "5"))
RAG_RELEVANCE_THRESHOLD: float = float(os.getenv("RAG_RELEVANCE_THRESHOLD", "0.7"))
RAG_MAX_CHUNK_SIZE: int = int(os.getenv("RAG_MAX_CHUNK_SIZE", "512"))

# ── Languages ─────────────────────────────────────────────────────────────────
SUPPORTED_LANGUAGES: list = os.getenv("SUPPORTED_LANGUAGES", "en,hi,te").split(",")

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "logs/finsaakhi.log")
AUDIT_LOG_FILE: str = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")

# ── Alert Thresholds ──────────────────────────────────────────────────────────
ALERT_HIGH_LATENCY_MS: int = int(os.getenv("ALERT_HIGH_LATENCY_MS", "5000"))
ALERT_LOW_SUCCESS_RATE: float = float(os.getenv("ALERT_LOW_SUCCESS_RATE", "80"))
ALERT_HIGH_ERROR_RATE: float = float(os.getenv("ALERT_HIGH_ERROR_RATE", "20"))
ALERT_EXCESSIVE_TOKENS: int = int(os.getenv("ALERT_EXCESSIVE_TOKENS", "10000"))
ALERT_LOW_RAG_RELEVANCE: float = float(os.getenv("ALERT_LOW_RAG_RELEVANCE", "0.5"))


# Placeholder strings that mean "not configured"
_PLACEHOLDERS = {
    "your_ibm_api_key_here", "your_ibm_project_id_here",
    "your_discovery_api_key_here", "change_me", "",
}


def is_ibm_configured() -> bool:
    """Return True only if all mandatory IBM credentials are set to real values."""
    return (
        bool(IBM_API_KEY)
        and IBM_API_KEY not in _PLACEHOLDERS
        and bool(IBM_PROJECT_ID)
        and IBM_PROJECT_ID not in _PLACEHOLDERS
        and bool(IBM_WATSONX_URL)
    )


def get_log_level() -> int:
    return getattr(logging, LOG_LEVEL.upper(), logging.INFO)
