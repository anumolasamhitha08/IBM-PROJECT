"""
middleware/rate_limiter.py – In-memory rate limiting for FinSakhi.
Prevents abuse of the chat API endpoint.
"""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Dict, Tuple

import config

logger = logging.getLogger("finsaakhi.ratelimit")

# Thread-safe storage
_lock = threading.Lock()
_request_log: Dict[str, deque] = {}   # session_id -> deque of timestamps

# Limits
MAX_REQUESTS_PER_WINDOW = getattr(config, "RATE_LIMIT_MAX_REQUESTS", 20)
WINDOW_SECONDS          = getattr(config, "RATE_LIMIT_WINDOW_SECONDS", 60)
MAX_REQUESTS_PER_HOUR   = getattr(config, "RATE_LIMIT_MAX_PER_HOUR", 60)

_hourly_log: Dict[str, deque] = {}   # session_id -> deque of hourly timestamps


class RateLimitResult:
    def __init__(self, allowed: bool, remaining: int, reset_in: float, reason: str = ""):
        self.allowed = allowed
        self.remaining = remaining
        self.reset_in = reset_in  # seconds until window resets
        self.reason = reason


def check_rate_limit(session_id: str) -> RateLimitResult:
    """
    Check if a request is allowed for the given session.
    Returns RateLimitResult with allowed=True if request proceeds.
    """
    now = time.time()

    with _lock:
        # ── Per-minute window ──────────────────────────────────────────────────
        if session_id not in _request_log:
            _request_log[session_id] = deque()
        window = _request_log[session_id]

        # Remove old entries outside window
        while window and (now - window[0]) > WINDOW_SECONDS:
            window.popleft()

        if len(window) >= MAX_REQUESTS_PER_WINDOW:
            reset_in = WINDOW_SECONDS - (now - window[0])
            logger.warning("Rate limit exceeded for session %s (%d req in %ds window)",
                           session_id[:8], len(window), WINDOW_SECONDS)
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_in=round(reset_in, 1),
                reason=f"Too many requests. Please wait {round(reset_in)} seconds.",
            )

        # ── Per-hour limit ─────────────────────────────────────────────────────
        if session_id not in _hourly_log:
            _hourly_log[session_id] = deque()
        hourly = _hourly_log[session_id]
        while hourly and (now - hourly[0]) > 3600:
            hourly.popleft()

        if len(hourly) >= MAX_REQUESTS_PER_HOUR:
            reset_in = 3600 - (now - hourly[0])
            logger.warning("Hourly rate limit exceeded for session %s", session_id[:8])
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_in=round(reset_in, 1),
                reason=f"Hourly limit reached. Please try again in {round(reset_in / 60)} minutes.",
            )

        # ── Allow ──────────────────────────────────────────────────────────────
        window.append(now)
        hourly.append(now)
        remaining = MAX_REQUESTS_PER_WINDOW - len(window)

    return RateLimitResult(allowed=True, remaining=remaining, reset_in=0.0)


def get_rate_limit_status(session_id: str) -> Dict:
    """Return current rate limit status for a session (for display)."""
    now = time.time()
    with _lock:
        window = _request_log.get(session_id, deque())
        recent = [t for t in window if (now - t) <= WINDOW_SECONDS]
        hourly = _hourly_log.get(session_id, deque())
        h_recent = [t for t in hourly if (now - t) <= 3600]
    return {
        "requests_in_window": len(recent),
        "window_max": MAX_REQUESTS_PER_WINDOW,
        "requests_in_hour": len(h_recent),
        "hourly_max": MAX_REQUESTS_PER_HOUR,
        "window_seconds": WINDOW_SECONDS,
    }


def cleanup_old_sessions(max_age_hours: int = 2):
    """Remove rate limit data for sessions inactive for more than max_age_hours."""
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    with _lock:
        stale = [sid for sid, q in _request_log.items()
                 if not q or q[-1] < cutoff]
        for sid in stale:
            _request_log.pop(sid, None)
            _hourly_log.pop(sid, None)
    if stale:
        logger.debug("Cleaned up %d stale rate limit sessions", len(stale))
