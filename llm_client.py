"""
llm_client.py – IBM Granite WatsonX AI client with monitoring instrumentation.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import config
from monitoring.llm_monitor import LLMCallContext, save_llm_call, track_llm_call

logger = logging.getLogger("finsaakhi.llm_client")

# ── Cached model instance ──────────────────────────────────────────────────────
_model_cache: Optional[Any] = None


def _get_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    if not config.is_ibm_configured():
        raise RuntimeError("IBM Granite credentials not configured. Check .env file.")
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params
        creds = Credentials(url=config.IBM_WATSONX_URL, api_key=config.IBM_API_KEY)
        _model_cache = ModelInference(
            model_id=config.IBM_GRANITE_MODEL_ID,
            credentials=creds,
            project_id=config.IBM_PROJECT_ID,
        )
        logger.info("IBM Granite model loaded: %s", config.IBM_GRANITE_MODEL_ID)
        return _model_cache
    except ImportError:
        raise RuntimeError("ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai")


def generate_response(
    prompt: str,
    agent_name: str = "",
    language: str = "en",
    request_category: str = None,
    max_new_tokens: int = 512,
    temperature: float = 0.1,
    retry_limit: int = 2,
) -> Tuple[str, LLMCallContext]:
    """
    Generate a response from IBM Granite with full monitoring.
    Returns (response_text, ctx) where ctx contains all metrics.
    Never logs the user prompt.
    """
    ctx = LLMCallContext(
        model_id=config.IBM_GRANITE_MODEL_ID,
        agent_name=agent_name,
        language=language,
    )
    ctx.request_category = request_category
    ctx.start()

    retries = 0
    last_error = None

    while retries <= retry_limit:
        try:
            model = _get_model()
            response = model.generate(
                prompt=prompt,
                params={
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "repetition_penalty": 1.1,
                    "stop_sequences": ["Human:", "User:", "\n\nHuman"],
                },
            )
            # Extract generated text
            generated = response.get("results", [{}])[0].get("generated_text", "").strip()

            # Extract token usage from response metadata
            usage = response.get("results", [{}])[0]
            input_tokens = usage.get("input_token_count", 0)
            output_tokens = usage.get("generated_token_count", 0)
            ctx.set_tokens(prompt=input_tokens, completion=output_tokens)
            ctx.finish(success=True)
            save_llm_call(ctx)
            return generated, ctx

        except Exception as exc:
            retries += 1
            ctx.retry_count = retries
            last_error = exc
            logger.warning("LLM call attempt %d failed: %s", retries, exc)
            if retries <= retry_limit:
                time.sleep(1.5 * retries)

    # All retries exhausted
    ctx.finish(
        success=False,
        error_type=type(last_error).__name__,
        error_message=str(last_error),
    )
    save_llm_call(ctx)
    raise last_error


def is_available() -> bool:
    """Quick check whether IBM Granite is configured and reachable."""
    if not config.is_ibm_configured():
        return False
    try:
        _get_model()
        return True
    except Exception:
        return False


def reset_model_cache():
    """Force re-initialisation of the model (useful after config changes)."""
    global _model_cache
    _model_cache = None
