"""
tests/test_dashboard_service.py – Tests for dashboard metrics service.
Run: pytest tests/ -v
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture(autouse=True)
def init_test_db():
    """Ensure the test database is initialized before tests."""
    from database import init_db
    init_db()


class TestDashboardService:
    """Test dashboard data service functions."""

    def _date_range(self):
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        return start, end

    def test_get_llm_summary_returns_dict(self):
        from monitoring.dashboard_service import get_llm_summary
        start, end = self._date_range()
        summary = get_llm_summary(start, end)
        assert isinstance(summary, dict)
        required_keys = ["total_requests", "successful", "failed", "success_rate"]
        for key in required_keys:
            assert key in summary, f"LLM summary missing key: {key}"

    def test_get_llm_summary_no_data(self):
        from monitoring.dashboard_service import get_llm_summary
        # Use future dates to ensure no data
        start = datetime(2099, 1, 1)
        end = datetime(2099, 12, 31)
        summary = get_llm_summary(start, end)
        assert summary["total_requests"] == 0
        assert summary["successful"] == 0
        assert summary["success_rate"] is None  # No data → N/A

    def test_get_rag_summary_returns_dict(self):
        from monitoring.dashboard_service import get_rag_summary
        start, end = self._date_range()
        summary = get_rag_summary(start, end)
        assert isinstance(summary, dict)
        assert "total_retrievals" in summary
        assert "grounded_rate" in summary

    def test_get_guardrail_summary_returns_dict(self):
        from monitoring.dashboard_service import get_guardrail_summary
        start, end = self._date_range()
        summary = get_guardrail_summary(start, end)
        assert isinstance(summary, dict)
        assert "total_triggers" in summary
        assert "by_type" in summary
        assert "critical" in summary

    def test_get_feedback_summary_returns_dict(self):
        from monitoring.dashboard_service import get_feedback_summary
        start, end = self._date_range()
        summary = get_feedback_summary(start, end)
        assert isinstance(summary, dict)
        assert "total_feedback" in summary
        assert "helpful_rate" in summary

    def test_get_overview_kpis_returns_dict(self):
        from monitoring.dashboard_service import get_overview_kpis
        start, end = self._date_range()
        kpis = get_overview_kpis(start, end)
        assert isinstance(kpis, dict)
        expected_keys = ["llm_total", "llm_success", "llm_failed", "total_tokens",
                        "agent_executions", "guardrail_triggers"]
        for key in expected_keys:
            assert key in kpis, f"Overview KPIs missing key: {key}"

    def test_date_range_presets(self):
        from monitoring.dashboard_service import _date_range
        now = datetime.utcnow()
        # Today
        start, end = _date_range("today")
        assert start.date() == now.date()
        # Last 7 days
        start7, end7 = _date_range("last_7")
        diff = end7 - start7
        assert 6 <= diff.days <= 7
        # Last 30 days
        start30, end30 = _date_range("last_30")
        diff30 = end30 - start30
        assert 29 <= diff30.days <= 30

    def test_save_feedback(self):
        from monitoring.dashboard_service import save_feedback, get_feedback_summary
        from datetime import datetime, timedelta
        import uuid
        request_id = str(uuid.uuid4())
        save_feedback(request_id, "helpful", "en")
        # Verify it was saved
        start = datetime.utcnow() - timedelta(minutes=1)
        end = datetime.utcnow() + timedelta(minutes=1)
        summary = get_feedback_summary(start, end)
        assert summary["helpful"] >= 1

    def test_get_llm_trend_df_returns_df(self):
        from monitoring.dashboard_service import get_llm_trend_df
        import pandas as pd
        start, end = self._date_range()
        df = get_llm_trend_df(start, end)
        assert isinstance(df, pd.DataFrame)

    def test_get_rag_trend_df_returns_df(self):
        from monitoring.dashboard_service import get_rag_trend_df
        import pandas as pd
        start, end = self._date_range()
        df = get_rag_trend_df(start, end)
        assert isinstance(df, pd.DataFrame)
