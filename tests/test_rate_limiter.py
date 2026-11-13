"""
tests/test_rate_limiter.py – Tests for rate limiting middleware.
Run: pytest tests/ -v
"""
from __future__ import annotations

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestRateLimiter:
    """Test rate limiting functionality."""

    def _fresh_session(self) -> str:
        """Generate a unique session ID for isolation."""
        import uuid
        return str(uuid.uuid4())

    def test_first_request_allowed(self):
        from middleware.rate_limiter import check_rate_limit
        session_id = self._fresh_session()
        result = check_rate_limit(session_id)
        assert result.allowed
        assert result.remaining >= 0

    def test_remaining_decreases(self):
        from middleware.rate_limiter import check_rate_limit
        session_id = self._fresh_session()
        r1 = check_rate_limit(session_id)
        r2 = check_rate_limit(session_id)
        assert r2.remaining < r1.remaining

    def test_rate_limit_enforced_after_max(self):
        """Force a rate limit by using a mock config with very low limit."""
        from middleware import rate_limiter
        session_id = self._fresh_session()

        # Patch the max to 3 for testing
        original_max = rate_limiter.MAX_REQUESTS_PER_WINDOW
        rate_limiter.MAX_REQUESTS_PER_WINDOW = 3
        try:
            for _ in range(3):
                result = check_result = rate_limiter.check_rate_limit(session_id)
            # 4th request should be blocked
            result = rate_limiter.check_rate_limit(session_id)
            assert not result.allowed
            assert result.reason
            assert result.reset_in > 0
        finally:
            rate_limiter.MAX_REQUESTS_PER_WINDOW = original_max

    def test_get_rate_limit_status(self):
        from middleware.rate_limiter import get_rate_limit_status, check_rate_limit
        session_id = self._fresh_session()
        check_rate_limit(session_id)
        status = get_rate_limit_status(session_id)
        assert status["requests_in_window"] == 1
        assert status["window_max"] > 0

    def test_different_sessions_independent(self):
        from middleware.rate_limiter import check_rate_limit
        s1 = self._fresh_session()
        s2 = self._fresh_session()
        r1 = check_rate_limit(s1)
        r2 = check_rate_limit(s2)
        assert r1.remaining == r2.remaining  # Both start fresh

    def test_cleanup_old_sessions(self):
        from middleware.rate_limiter import cleanup_old_sessions
        # Should not raise
        cleanup_old_sessions(max_age_hours=0)
