"""
dashboard.py – FinSakhi Admin Monitoring Dashboard (Streamlit).
Run: streamlit run dashboard.py
All metrics derived from real DB data. No fabricated values.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timedelta, date
from typing import Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

os.makedirs("logs", exist_ok=True)
import config
from database import init_db
init_db()

from auth import is_authenticated, login_page, logout
from monitoring.dashboard_service import (
    _date_range,
    get_agent_executions_df,
    get_agent_summary_df,
    get_feedback_summary,
    get_guardrail_df,
    get_guardrail_summary,
    get_llm_summary,
    get_llm_trend_df,
    get_overview_kpis,
    get_rag_summary,
    get_rag_trend_df,
    get_traces_df,
    get_trace_steps,
)

logger = logging.getLogger("finsaakhi.dashboard")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSakhi Admin Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body { font-family: -apple-system, "Segoe UI", system-ui, sans-serif; }

/* KPI Cards */
.kpi-card {
    background: #f7f8fa; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 1.2rem 1rem;
    text-align: center; min-height: 110px;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
}
.kpi-value { font-size: 2rem; font-weight: 700; color: #1a56db; line-height: 1.1; }
.kpi-label { font-size: 0.78rem; color: #57606a; margin-top: 0.3rem; font-weight: 500; }
.kpi-delta { font-size: 0.75rem; margin-top: 0.2rem; }
.kpi-ok { color: #16a34a; }
.kpi-warn { color: #d97706; }
.kpi-err { color: #dc2626; }

/* Section headers */
.section-header {
    font-size: 1.25rem; font-weight: 700; color: #1f2328;
    border-left: 4px solid #1a56db; padding-left: 0.75rem;
    margin: 1.5rem 0 1rem;
}

/* Status badges */
.badge-ok { background:#dcfce7; color:#166534; padding:2px 8px; border-radius:10px; font-size:0.75rem; font-weight:600; }
.badge-warn { background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:10px; font-size:0.75rem; font-weight:600; }
.badge-err { background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:10px; font-size:0.75rem; font-weight:600; }

/* Alert box */
.alert-box {
    background: #fff7ed; border: 1px solid #fed7aa;
    border-radius: 8px; padding: 0.75rem 1rem;
    margin: 0.5rem 0; font-size: 0.875rem; color: #9a3412;
}
.alert-critical {
    background: #fee2e2; border-color: #fca5a5; color: #991b1b;
}

/* Empty state */
.empty-state {
    text-align: center; padding: 3rem; color: #57606a;
    background: #f7f8fa; border-radius: 12px;
    border: 1px dashed #e5e7eb;
}

/* Nav item */
.nav-active { background: #eff6ff; border-radius: 8px; padding: 4px 0; }

/* IBM badge */
.ibm-granite-badge {
    background: #161616; color: white;
    padding: 4px 12px; border-radius: 6px;
    font-size: 0.75rem; font-weight: 600;
    display: inline-block; margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Auth Gate ──────────────────────────────────────────────────────────────────
if not is_authenticated():
    login_page()
    st.stop()

# ── Sidebar Navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 FinSakhi Admin")
    st.markdown(f'<div class="ibm-granite-badge">IBM Granite Monitoring</div>', unsafe_allow_html=True)
    st.caption(f"Logged in as: **{st.session_state.get('admin_user', 'admin')}**")

    # IBM status
    ibm_ok = config.is_ibm_configured()
    status_icon = "🟢" if ibm_ok else "🔴"
    st.markdown(f"{status_icon} IBM Granite: {'Connected' if ibm_ok else '**Not Connected**'}")
    st.divider()

    nav = st.radio(
        "Navigation",
        [
            "📋 Overview",
            "🤖 LLM Analytics",
            "🧠 Agent Analytics",
            "🔍 RAG Analytics",
            "⭐ Response Quality",
            "🛡️ Guardrail Analytics",
            "🔬 Execution Traces",
            "⚙️ System Health",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # ── Date Filter ────────────────────────────────────────────────────────────
    st.markdown("**📅 Date Filter**")
    date_preset = st.selectbox(
        "Period",
        ["Today", "Last 7 Days", "Last 30 Days", "Custom"],
        label_visibility="collapsed",
    )

    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None
    if date_preset == "Custom":
        c1, c2 = st.columns(2)
        with c1:
            cs = st.date_input("From", value=date.today() - timedelta(days=7))
        with c2:
            ce = st.date_input("To", value=date.today())
        custom_start = datetime.combine(cs, datetime.min.time())
        custom_end = datetime.combine(ce, datetime.max.time())

    preset_map = {
        "Today": "today",
        "Last 7 Days": "last_7",
        "Last 30 Days": "last_30",
        "Custom": "custom",
    }
    date_start, date_end = _date_range(preset_map[date_preset], custom_start, custom_end)

    st.divider()

    # ── CSV Export ─────────────────────────────────────────────────────────────
    st.markdown("**📥 Download Reports**")
    try:
        llm_df_export = get_llm_trend_df(date_start, date_end)
        rag_df_export = get_rag_trend_df(date_start, date_end)
        guard_df_export = get_guardrail_df(date_start, date_end)
        agent_df_export = get_agent_executions_df(date_start, date_end)

        if not llm_df_export.empty:
            st.download_button(
                "📊 LLM Requests CSV",
                llm_df_export.to_csv(index=False).encode("utf-8"),
                file_name=f"finsaakhi_llm_{date_start.date()}_to_{date_end.date()}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        if not rag_df_export.empty:
            st.download_button(
                "🔍 RAG Events CSV",
                rag_df_export.to_csv(index=False).encode("utf-8"),
                file_name=f"finsaakhi_rag_{date_start.date()}_to_{date_end.date()}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        if not guard_df_export.empty:
            st.download_button(
                "🛡️ Guardrail Events CSV",
                guard_df_export.to_csv(index=False).encode("utf-8"),
                file_name=f"finsaakhi_guardrails_{date_start.date()}_to_{date_end.date()}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        if not agent_df_export.empty:
            st.download_button(
                "🧠 Agent Executions CSV",
                agent_df_export.to_csv(index=False).encode("utf-8"),
                file_name=f"finsaakhi_agents_{date_start.date()}_to_{date_end.date()}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        if all(df.empty for df in [llm_df_export, rag_df_export, guard_df_export, agent_df_export]):
            st.caption("No data in selected period to export.")
    except Exception as _csv_err:
        st.caption(f"CSV export unavailable: {_csv_err}")

    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        logout()


# ── Helper: n/a formatter ──────────────────────────────────────────────────────
def fmt(val, suffix="", decimals=1):
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:.{decimals}f}{suffix}"
    return f"{val}{suffix}"


def kpi_card(label: str, value, suffix: str = "", color_class: str = ""):
    val_str = fmt(value, suffix)
    cls = f"kpi-value {color_class}" if color_class else "kpi-value"
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="{cls}">{val_str}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def empty_state(msg: str = "No monitoring data available yet."):
    st.markdown(f'<div class="empty-state">📭 {msg}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if nav == "📋 Overview":
    st.title("📋 Dashboard Overview")
    st.caption(f"Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")

    if not ibm_ok:
        st.warning("⚠️ **IBM Granite not connected.** Set IBM_API_KEY and IBM_PROJECT_ID in .env to see real LLM metrics.")

    kpis = get_overview_kpis(date_start, date_end)

    # ── KPI Row 1 ──────────────────────────────────────────────────────────────
    section("Key Performance Indicators")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Total LLM Requests", kpis["llm_total"])
    with c2: kpi_card("Successful LLM Requests", kpis["llm_success"], color_class="kpi-ok")
    with c3: kpi_card("Failed LLM Requests", kpis["llm_failed"], color_class="kpi-err" if kpis["llm_failed"] > 0 else "")
    with c4: kpi_card("LLM Success Rate", kpis["llm_success_rate"], "%")
    with c5: kpi_card("Avg Response Latency", kpis["avg_latency_ms"], " ms")

    c6, c7, c8, c9, c10 = st.columns(5)
    with c6: kpi_card("Total Tokens Used", kpis["total_tokens"])
    with c7: kpi_card("Agent Executions", kpis["agent_executions"])
    with c8: kpi_card("Agent Success Rate", kpis["agent_success_rate"], "%")
    with c9: kpi_card("RAG Retrieval Rate", kpis["rag_success_rate"], "%")
    with c10: kpi_card("Guardrail Triggers", kpis["guardrail_triggers"], color_class="kpi-warn" if kpis["guardrail_triggers"] > 0 else "")

    # ── IBM Granite Status ─────────────────────────────────────────────────────
    section("IBM Granite Status")
    if not ibm_ok:
        st.error("🔴 **IBM Granite not connected** — Configure credentials in .env file.\n\nIBM_API_KEY, IBM_PROJECT_ID, IBM_WATSONX_URL are required.")
    else:
        st.success(f"🟢 IBM Granite connected — Model: `{config.IBM_GRANITE_MODEL_ID}`")

    # ── Quick trend ────────────────────────────────────────────────────────────
    section("Request Trend (Last Period)")
    llm_df = get_llm_trend_df(date_start, date_end)
    if llm_df.empty:
        empty_state()
    else:
        llm_df["date"] = pd.to_datetime(llm_df["timestamp"]).dt.date
        daily = llm_df.groupby(["date", "success"]).size().reset_index(name="count")
        fig = px.line(
            daily, x="date", y="count", color="success",
            labels={"count": "Requests", "date": "Date", "success": "Success"},
            color_discrete_map={True: "#16a34a", False: "#dc2626"},
            title="LLM Requests Over Time",
        )
        fig.update_layout(height=300, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # ── Alerts ────────────────────────────────────────────────────────────────
    section("Active Alerts")
    alerts = []
    if not ibm_ok:
        alerts.append(("critical", "IBM Granite API not configured."))
    if kpis["llm_failed"] and kpis["llm_total"] and (kpis["llm_failed"] / kpis["llm_total"]) > (config.ALERT_HIGH_ERROR_RATE / 100):
        alerts.append(("warning", f"High LLM error rate: {fmt(kpis['llm_failed'] / max(kpis['llm_total'],1) * 100,'%')}"))
    if kpis["avg_latency_ms"] and kpis["avg_latency_ms"] > config.ALERT_HIGH_LATENCY_MS:
        alerts.append(("warning", f"High response latency: {fmt(kpis['avg_latency_ms'],' ms')}"))
    if kpis["guardrail_triggers"] and kpis["guardrail_triggers"] > 10:
        alerts.append(("warning", f"High guardrail activity: {kpis['guardrail_triggers']} triggers"))

    if alerts:
        for level, msg in alerts:
            cls = "alert-critical" if level == "critical" else "alert-box"
            icon = "🚨" if level == "critical" else "⚠️"
            st.markdown(f'<div class="{cls}">{icon} {msg}</div>', unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – LLM ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "🤖 LLM Analytics":
    st.title("🤖 IBM Granite LLM Analytics")
    st.caption(f"Model: `{config.IBM_GRANITE_MODEL_ID}` | Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")

    if not ibm_ok:
        st.error("🔴 IBM Granite not connected. Metrics below reflect only cached/test calls.")

    summary = get_llm_summary(date_start, date_end)
    llm_df = get_llm_trend_df(date_start, date_end)

    # KPI row
    section("LLM Performance Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Requests", summary["total_requests"])
    with c2: kpi_card("Successful", summary["successful"], color_class="kpi-ok")
    with c3: kpi_card("Failed", summary["failed"], color_class="kpi-err" if summary["failed"] > 0 else "")
    with c4: kpi_card("Success Rate", summary["success_rate"], "%")

    c5, c6, c7, c8 = st.columns(4)
    with c5: kpi_card("Avg Latency", summary["avg_latency_ms"], " ms")
    with c6: kpi_card("Min Latency", summary["min_latency_ms"], " ms")
    with c7: kpi_card("Max Latency", summary["max_latency_ms"], " ms")
    with c8: kpi_card("Total Tokens", summary["total_tokens"])

    if llm_df.empty:
        st.divider()
        empty_state("No LLM calls recorded yet. Start using FinSakhi chat to generate data.")
    else:
        llm_df["timestamp"] = pd.to_datetime(llm_df["timestamp"])

        # ── Chart 1: Request trend ─────────────────────────────────────────────
        section("LLM Request Trend")
        llm_df["date"] = llm_df["timestamp"].dt.date
        trend = llm_df.groupby(["date", "success"]).size().reset_index(name="requests")
        fig1 = px.line(
            trend, x="date", y="requests", color="success",
            color_discrete_map={True: "#16a34a", False: "#dc2626"},
            labels={"requests": "Count", "date": "Date", "success": "Success"},
            title="LLM Requests Over Time",
        )
        fig1.update_layout(height=320)
        st.plotly_chart(fig1, use_container_width=True)

        # ── Chart 2: Latency ───────────────────────────────────────────────────
        section("Response Latency")
        success_df = llm_df[llm_df["success"] == True].copy()
        if not success_df.empty:
            fig2 = px.line(
                success_df.sort_values("timestamp"),
                x="timestamp", y="latency_ms",
                title="Response Latency Over Time (successful calls)",
                labels={"latency_ms": "Latency (ms)", "timestamp": "Time"},
            )
            fig2.add_hline(y=config.ALERT_HIGH_LATENCY_MS, line_dash="dash", line_color="red",
                          annotation_text="Alert threshold")
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            empty_state("No successful calls to show latency for.")

        # ── Chart 3: Token usage ───────────────────────────────────────────────
        section("Token Consumption")
        token_df = llm_df[llm_df["total_tokens"] > 0].copy()
        if not token_df.empty:
            token_df["date"] = token_df["timestamp"].dt.date
            daily_tokens = token_df.groupby("date")["total_tokens"].sum().reset_index()
            fig3 = px.bar(
                daily_tokens, x="date", y="total_tokens",
                title="Daily Token Consumption",
                labels={"total_tokens": "Tokens", "date": "Date"},
                color_discrete_sequence=["#1a56db"],
            )
            fig3.update_layout(height=300)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("ℹ️ Token data not yet available. Token counts are captured from actual IBM Granite API responses.")

        # ── Chart 4: Success vs failure ────────────────────────────────────────
        section("Success vs Failure")
        pie_data = pd.DataFrame({
            "status": ["Success", "Failed"],
            "count": [summary["successful"], summary["failed"]],
        })
        if pie_data["count"].sum() > 0:
            fig4 = px.pie(
                pie_data, values="count", names="status",
                color="status",
                color_discrete_map={"Success": "#16a34a", "Failed": "#dc2626"},
                title="Success vs Failure Distribution",
            )
            fig4.update_layout(height=320)
            st.plotly_chart(fig4, use_container_width=True)

        # ── Raw data table ─────────────────────────────────────────────────────
        section("Recent LLM Calls")
        display_df = llm_df[["timestamp", "success", "latency_ms", "total_tokens", "agent_name", "language"]].copy()
        display_df["success"] = display_df["success"].map({True: "✅", False: "❌"})
        display_df = display_df.rename(columns={
            "timestamp": "Time", "success": "Status", "latency_ms": "Latency(ms)",
            "total_tokens": "Tokens", "agent_name": "Agent", "language": "Lang",
        })
        st.dataframe(display_df.head(50), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – AGENT ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "🧠 Agent Analytics":
    st.title("🧠 Individual Agent Performance")
    st.caption(f"Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")

    agent_summary = get_agent_summary_df(date_start, date_end)

    if agent_summary.empty:
        empty_state("No agent execution data yet. Use the chat interface to generate data.")
    else:
        section("Agent Summary")
        # KPI cards per agent
        num_agents = len(agent_summary)
        if num_agents <= 4:
            cols = st.columns(num_agents)
        else:
            cols = st.columns(4)
            cols = cols + st.columns(num_agents - 4)
        for i, (_, row) in enumerate(agent_summary.iterrows()):
            with cols[i % 4]:
                rate = row.get("success_rate")
                color = "kpi-ok" if (rate and rate >= 80) else "kpi-err"
                kpi_card(row["agent_name"].replace("Agent", ""), fmt(rate, "%"), color_class=color)

        section("Agent Comparison Table")
        display_cols = ["agent_name", "total_executions", "successful", "failed",
                       "success_rate", "avg_time_ms", "total_llm_calls", "total_tokens"]
        show_df = agent_summary[display_cols].copy()
        show_df.columns = ["Agent", "Total", "Success", "Failed", "Success Rate %",
                           "Avg Time (ms)", "LLM Calls", "Tokens"]
        st.dataframe(show_df.round(1), use_container_width=True)

        # ── Chart: Agent success rate bar ──────────────────────────────────────
        section("Agent Success Rate")
        fig_agents = px.bar(
            agent_summary, x="agent_name", y="success_rate",
            color="success_rate",
            color_continuous_scale=["#dc2626", "#f59e0b", "#16a34a"],
            range_color=[0, 100],
            labels={"agent_name": "Agent", "success_rate": "Success Rate (%)"},
            title="Agent Success Rate Comparison",
        )
        fig_agents.add_hline(y=config.ALERT_LOW_SUCCESS_RATE, line_dash="dash",
                            line_color="orange", annotation_text="Alert threshold")
        fig_agents.update_layout(height=350)
        st.plotly_chart(fig_agents, use_container_width=True)

        # ── Chart: Execution distribution pie ─────────────────────────────────
        section("Agent Execution Distribution")
        fig_pie = px.pie(
            agent_summary, values="total_executions", names="agent_name",
            title="Agent Execution Distribution",
        )
        fig_pie.update_layout(height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

        # ── Individual agent drill-down ────────────────────────────────────────
        section("Individual Agent Inspector")
        agent_names = agent_summary["agent_name"].tolist()
        selected_agent = st.selectbox("Select Agent", agent_names)
        if selected_agent:
            agent_df = get_agent_executions_df(date_start, date_end, agent_name=selected_agent)
            if agent_df.empty:
                empty_state(f"No execution data for {selected_agent} in this period.")
            else:
                row = agent_summary[agent_summary["agent_name"] == selected_agent].iloc[0]
                mc1, mc2, mc3, mc4 = st.columns(4)
                with mc1: kpi_card("Total Executions", int(row["total_executions"]))
                with mc2: kpi_card("Success Rate", fmt(row["success_rate"], "%"))
                with mc3: kpi_card("Avg Time", fmt(row["avg_time_ms"], " ms"))
                with mc4: kpi_card("Total Tokens", int(row["total_tokens"]))

                fig_agent = px.scatter(
                    agent_df, x="timestamp", y="execution_time_ms",
                    color="success", color_discrete_map={True: "#16a34a", False: "#dc2626"},
                    title=f"{selected_agent} – Execution Timeline",
                    labels={"execution_time_ms": "Duration (ms)", "timestamp": "Time"},
                )
                fig_agent.update_layout(height=300)
                st.plotly_chart(fig_agent, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – RAG ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "🔍 RAG Analytics":
    st.title("🔍 RAG Pipeline Performance")
    st.caption(f"Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")

    rag_sum = get_rag_summary(date_start, date_end)
    rag_df = get_rag_trend_df(date_start, date_end)

    section("RAG Performance KPIs")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Total Retrievals", rag_sum["total_retrievals"])
    with c2: kpi_card("Successful", rag_sum["successful"], color_class="kpi-ok")
    with c3: kpi_card("Failed", rag_sum["failed"], color_class="kpi-err" if rag_sum["failed"] > 0 else "")
    with c4: kpi_card("Success Rate", rag_sum["success_rate"], "%")
    with c5: kpi_card("Avg Latency", rag_sum["avg_latency_ms"], " ms")

    c6, c7, c8, c9, c10 = st.columns(5)
    with c6: kpi_card("Avg Docs Retrieved", rag_sum["avg_docs"])
    with c7: kpi_card("Avg Relevance Score", fmt(rag_sum["avg_relevance"]))
    with c8: kpi_card("Grounded Response Rate", rag_sum["grounded_rate"], "%")
    with c9: kpi_card("Empty Retrievals", rag_sum["empty_retrievals"], color_class="kpi-warn" if rag_sum["empty_retrievals"] > 0 else "")
    with c10: kpi_card("Doc Validation Failures", rag_sum["doc_validation_failures"], color_class="kpi-err" if rag_sum["doc_validation_failures"] > 0 else "")

    if rag_df.empty:
        st.divider()
        empty_state("No RAG events recorded yet.")
    else:
        rag_df["timestamp"] = pd.to_datetime(rag_df["timestamp"])

        section("RAG Retrieval Performance Over Time")
        rag_df["date"] = rag_df["timestamp"].dt.date
        daily_rag = rag_df.groupby("date").agg(
            total=("success", "count"),
            successful=("success", "sum"),
            avg_relevance=("relevance", "mean"),
        ).reset_index()
        daily_rag["success_rate"] = (daily_rag["successful"] / daily_rag["total"] * 100).round(1)

        fig_rag = go.Figure()
        fig_rag.add_trace(go.Scatter(x=daily_rag["date"], y=daily_rag["success_rate"],
                                    mode="lines+markers", name="Success Rate %", line=dict(color="#16a34a")))
        fig_rag.add_trace(go.Scatter(x=daily_rag["date"], y=daily_rag["avg_relevance"] * 100,
                                    mode="lines+markers", name="Avg Relevance × 100", line=dict(color="#1a56db")))
        fig_rag.update_layout(title="RAG Success Rate & Relevance", height=320)
        st.plotly_chart(fig_rag, use_container_width=True)

        section("Groundedness vs Latency")
        fig_scatter = px.scatter(
            rag_df, x="latency_ms", y="relevance",
            color="grounded",
            color_discrete_map={True: "#16a34a", False: "#dc2626"},
            labels={"latency_ms": "Retrieval Latency (ms)", "relevance": "Relevance Score"},
            title="Retrieval Latency vs Relevance Score",
        )
        fig_scatter.add_hline(y=config.RAG_RELEVANCE_THRESHOLD, line_dash="dash",
                             annotation_text="Min relevance threshold")
        fig_scatter.update_layout(height=320)
        st.plotly_chart(fig_scatter, use_container_width=True)

        section("Recent RAG Events")
        show = rag_df[["timestamp", "success", "docs", "relevance", "latency_ms", "grounded"]].copy()
        show["success"] = show["success"].map({True: "✅", False: "❌"})
        show["grounded"] = show["grounded"].map({True: "✅", False: "❌"})
        st.dataframe(show.head(50).rename(columns={
            "timestamp": "Time", "success": "Status", "docs": "Docs",
            "relevance": "Relevance", "latency_ms": "Latency(ms)", "grounded": "Grounded",
        }), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 – RESPONSE QUALITY (LLM Evaluation Dashboard)
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "⭐ Response Quality":
    st.title("⭐ LLM Response Quality Evaluation")
    st.caption(f"Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")
    st.info("""
    **Evaluation Method:** Response quality is assessed via:
    1. **User feedback** (Helpful / Not Helpful / Report Incorrect)
    2. **Groundedness** (does the response cite retrieved documents?)
    3. **Hallucination indicators** (uncertainty language detected in output)
    
    ⚠️ Automated scores are **estimates** and are NOT a substitute for human review.
    An LLM-generated answer is not labelled correct simply because the LLM produced it.
    """)

    feedback = get_feedback_summary(date_start, date_end)

    section("Feedback KPIs")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Total Feedback", feedback["total_feedback"])
    with c2: kpi_card("Helpful", feedback["helpful"], color_class="kpi-ok")
    with c3: kpi_card("Not Helpful", feedback["not_helpful"], color_class="kpi-warn")
    with c4: kpi_card("Reported Incorrect", feedback["incorrect"], color_class="kpi-err" if feedback["incorrect"] > 0 else "")
    with c5: kpi_card("Helpful Rate", feedback["helpful_rate"], "%", color_class="kpi-ok" if (feedback["helpful_rate"] or 0) >= 70 else "kpi-warn")

    section("Quality Metrics")
    c6, c7, c8 = st.columns(3)
    with c6: kpi_card("Avg Answer Relevance", fmt(feedback["avg_relevance"]))
    with c7: kpi_card("Avg Groundedness", fmt(feedback["avg_groundedness"]))
    with c8: kpi_card("Hallucination Flags", feedback["hallucination_count"], color_class="kpi-err" if feedback["hallucination_count"] > 0 else "")

    if feedback["total_feedback"] == 0:
        st.divider()
        empty_state("No user feedback collected yet. Use the 👍/👎/⚠️ buttons in the chat to provide feedback.")
    else:
        section("User Feedback Distribution")
        fb_pie = pd.DataFrame({
            "category": ["Helpful", "Not Helpful", "Reported Incorrect"],
            "count": [feedback["helpful"], feedback["not_helpful"], feedback["incorrect"]],
        })
        fig_fb = px.pie(
            fb_pie, values="count", names="category",
            color="category",
            color_discrete_map={"Helpful": "#16a34a", "Not Helpful": "#d97706", "Reported Incorrect": "#dc2626"},
            title="User Feedback Distribution",
        )
        fig_fb.update_layout(height=360)
        st.plotly_chart(fig_fb, use_container_width=True)

    section("Evaluation Dimensions")
    st.markdown("""
    | Dimension | Method | Notes |
    |-----------|--------|-------|
    | **Answer Relevance** | User feedback | Scores from 👍/👎 |
    | **Groundedness** | RAG overlap check | Does answer reference retrieved docs? |
    | **Faithfulness** | Output guardrail | No claims beyond retrieved sources |
    | **Financial Accuracy** | Unsafe advice detector | Blocks fabricated rates/guarantees |
    | **Language Correctness** | Language detection | Checks correct language used |
    | **Citation Quality** | Source presence check | Did response cite sources? |
    | **Hallucination Risk** | Uncertainty language scan | Flags "I think", "might be" patterns |
    
    > All automated scores are heuristic estimates. Ground truth requires human expert validation.
    """)

    # ── RAG Grounded Response Rate chart ──────────────────────────────────────
    section("RAG Grounded Response Rate")
    rag_sum = get_rag_summary(date_start, date_end)
    rag_df = get_rag_trend_df(date_start, date_end)
    if not rag_df.empty:
        rag_df["date"] = pd.to_datetime(rag_df["timestamp"]).dt.date
        grounded_daily = rag_df.groupby("date").agg(
            total=("grounded", "count"),
            grounded=("grounded", "sum"),
        ).reset_index()
        grounded_daily["rate"] = (grounded_daily["grounded"] / grounded_daily["total"] * 100).round(1)
        fig_gr = px.line(
            grounded_daily, x="date", y="rate",
            labels={"rate": "Grounded Rate (%)", "date": "Date"},
            title="Grounded Response Rate Over Time",
        )
        fig_gr.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="80% target")
        fig_gr.update_layout(height=300)
        st.plotly_chart(fig_gr, use_container_width=True)
    else:
        empty_state("No RAG data available to compute grounded response rate.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 – GUARDRAIL ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "🛡️ Guardrail Analytics":
    st.title("🛡️ Guardrail Performance Monitoring")
    st.caption(f"Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")
    st.info("🔒 Sensitive values (OTPs, PINs, CVVs, passwords) are **never stored or displayed**. Only event type and severity are recorded.")

    guardrail_sum = get_guardrail_summary(date_start, date_end)
    guardrail_df = get_guardrail_df(date_start, date_end)

    section("Guardrail KPIs")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Triggers", guardrail_sum["total_triggers"])
    with c2: kpi_card("Critical Severity", guardrail_sum["critical"], color_class="kpi-err" if guardrail_sum["critical"] > 0 else "")
    with c3: kpi_card("High Severity", guardrail_sum["high"], color_class="kpi-warn" if guardrail_sum["high"] > 0 else "")

    by_type = guardrail_sum["by_type"]
    with c4: kpi_card("Privacy Events", by_type.get("privacy", 0), color_class="kpi-err" if by_type.get("privacy", 0) > 0 else "")

    section("Triggers by Guardrail Type")
    if by_type:
        type_df = pd.DataFrame(list(by_type.items()), columns=["type", "count"])
        fig_gt = px.bar(
            type_df, x="type", y="count",
            labels={"type": "Guardrail Type", "count": "Events"},
            color="type",
            title="Guardrail Events by Type",
        )
        fig_gt.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_gt, use_container_width=True)

    if not guardrail_df.empty:
        section("Guardrail Event Timeline")
        guardrail_df["date"] = pd.to_datetime(guardrail_df["timestamp"]).dt.date
        daily_g = guardrail_df.groupby(["date", "type"]).size().reset_index(name="count")
        fig_gtime = px.bar(
            daily_g, x="date", y="count", color="type",
            title="Guardrail Events Over Time",
            labels={"count": "Events", "date": "Date"},
        )
        fig_gtime.update_layout(height=320)
        st.plotly_chart(fig_gtime, use_container_width=True)

        section("Guardrail Event Log")
        show_g = guardrail_df[["timestamp", "type", "trigger", "severity", "action", "language"]].copy()
        show_g = show_g.rename(columns={
            "timestamp": "Time", "type": "Type", "trigger": "Trigger",
            "severity": "Severity", "action": "Action", "language": "Lang",
        })
        st.dataframe(show_g.head(100), use_container_width=True)

        # ── Security Alerts ────────────────────────────────────────────────────
        section("Security Alert Summary")
        critical_events = guardrail_df[guardrail_df["severity"] == "critical"]
        if not critical_events.empty:
            for _, ev in critical_events.head(10).iterrows():
                st.markdown(
                    f'<div class="alert-critical">🚨 <b>{ev["trigger"]}</b> ({ev["type"]}) at {ev["timestamp"]} — Action: {ev["action"]}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No critical security events in this period.")
    else:
        empty_state("No guardrail events recorded yet.")

    section("Guardrail Coverage Summary")
    st.markdown("""
    | Guardrail Layer | Coverage | Key Triggers |
    |----------------|----------|--------------|
    | **Input** | ✅ Active | Prompt injection, jailbreak, off-topic, sensitive data |
    | **Output** | ✅ Active | Unsafe advice, credential leakage, hallucination flags |
    | **RAG** | ✅ Active | Document injection, untrusted sources, low relevance |
    | **Agent** | ✅ Active | Execution limits, unauthorized tool access, permission violations |
    | **Tool** | ✅ Active | Rate limits, timeout, unauthorized API access |
    | **Privacy** | ✅ Active | OTP/PIN/CVV masking, no sensitive logging |
    | **App Security** | ✅ Active | Session auth, input XSS prevention, error handling |
    | **Human-in-Loop** | ✅ Active | Fraud escalation to 1930, feedback reporting |
    | **Operational** | ✅ Active | IBM Granite monitoring, retry limits, audit logs |
    """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 – EXECUTION TRACES
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "🔬 Execution Traces":
    st.title("🔬 Agent Execution Trace Viewer")
    st.caption(f"Period: {date_start.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}")
    st.warning("🔒 User prompts and personal financial information are NOT stored or displayed here.")

    traces_df = get_traces_df(date_start, date_end)

    if traces_df.empty:
        empty_state("No execution traces yet. Use the chat interface to generate traces.")
    else:
        section("Execution Overview")
        ec1, ec2, ec3, ec4 = st.columns(4)
        total_traces = len(traces_df)
        success_traces = traces_df["success"].sum()
        with ec1: kpi_card("Total Traces", total_traces)
        with ec2: kpi_card("Successful", int(success_traces), color_class="kpi-ok")
        with ec3: kpi_card("Failed", int(total_traces - success_traces), color_class="kpi-err" if (total_traces - success_traces) > 0 else "")
        avg_dur = traces_df[traces_df["success"] == True]["duration_ms"].mean()
        with ec4: kpi_card("Avg Duration", fmt(avg_dur, " ms"))

        section("Execution Trace Log")
        display_traces = traces_df.copy()
        display_traces["success"] = display_traces["success"].map({True: "✅", False: "❌"})
        st.dataframe(
            display_traces[["trace_id", "category", "language", "duration_ms",
                           "llm_calls", "tool_calls", "tokens", "guardrails", "success", "timestamp"]].rename(columns={
                "trace_id": "Trace ID", "category": "Category", "language": "Lang",
                "duration_ms": "Duration(ms)", "llm_calls": "LLM Calls",
                "tool_calls": "Tool Calls", "tokens": "Tokens",
                "guardrails": "Guardrails", "success": "Status", "timestamp": "Time",
            }),
            use_container_width=True,
        )

        section("Inspect Execution Steps")
        trace_ids = traces_df["trace_id"].tolist()
        selected_trace = st.selectbox("Select Trace ID", trace_ids)
        if selected_trace:
            trace_prefix = selected_trace.replace("...", "")
            steps = get_trace_steps(trace_prefix)
            if steps:
                st.markdown("**Execution Flow:**")
                # Visual pipeline
                pipeline_steps = [s["step"] for s in steps]
                arrows = " → ".join(f"`{s}`" for s in pipeline_steps)
                st.markdown(arrows)
                st.divider()
                # Step details table
                step_df = pd.DataFrame(steps)
                st.dataframe(step_df.rename(columns={
                    "step": "Step", "status": "Status",
                    "duration_ms": "Duration(ms)", "ts": "Timestamp",
                }), use_container_width=True)
            else:
                st.info("Step details not available for this trace.")

        section("Duration Distribution")
        fig_dur = px.histogram(
            traces_df, x="duration_ms", nbins=20,
            title="Request Duration Distribution",
            labels={"duration_ms": "Duration (ms)"},
            color_discrete_sequence=["#1a56db"],
        )
        fig_dur.update_layout(height=300)
        st.plotly_chart(fig_dur, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 – SYSTEM HEALTH
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "⚙️ System Health":
    st.title("⚙️ System Health Monitor")

    from monitoring.system_monitor import full_health_check

    if st.button("🔄 Run Health Check"):
        with st.spinner("Checking systems..."):
            health = full_health_check()
        st.session_state["last_health"] = health

    health = st.session_state.get("last_health", None)
    if health is None:
        st.info("Click **Run Health Check** to check system status.")
    else:
        section("Component Status")
        h1, h2, h3 = st.columns(3)

        def status_badge(status: str) -> str:
            if status == "ok":
                return "🟢 Online"
            elif status == "degraded":
                return "🟡 Degraded"
            else:
                return "🔴 Offline"

        with h1:
            ibm = health["ibm_granite"]
            st.markdown("**IBM Granite**")
            st.markdown(status_badge(ibm["status"]))
            if ibm.get("latency_ms"):
                st.caption(f"Latency: {ibm['latency_ms']} ms")
            st.caption(ibm.get("message", "")[:100])

        with h2:
            db = health["database"]
            st.markdown("**Database**")
            st.markdown(status_badge(db["status"]))
            if db.get("latency_ms"):
                st.caption(f"Latency: {db['latency_ms']} ms")

        with h3:
            vdb = health["vector_db"]
            st.markdown("**Vector DB (ChromaDB)**")
            st.markdown(status_badge(vdb["status"]))

        section("System Resources")
        res = health.get("resources", {})
        r1, r2, r3, r4 = st.columns(4)
        with r1: kpi_card("CPU Usage", fmt(res.get("cpu_percent"), "%"))
        with r2: kpi_card("Memory Usage", fmt(res.get("memory_percent"), "%"))
        with r3: kpi_card("Memory Used (MB)", fmt(res.get("memory_used_mb"), " MB"))
        with r4: kpi_card("Memory Total (MB)", fmt(res.get("memory_total_mb"), " MB"))

        st.caption(f"Last checked: {health.get('checked_at', 'N/A')}")

    section("Alert Thresholds (Configurable)")
    st.markdown(f"""
    | Threshold | Value |
    |-----------|-------|
    | High Latency Alert | `{config.ALERT_HIGH_LATENCY_MS} ms` |
    | Low Success Rate Alert | `{config.ALERT_LOW_SUCCESS_RATE}%` |
    | High Error Rate Alert | `{config.ALERT_HIGH_ERROR_RATE}%` |
    | Excessive Token Alert | `{config.ALERT_EXCESSIVE_TOKENS} tokens` |
    | Low RAG Relevance Alert | `{config.ALERT_LOW_RAG_RELEVANCE}` |
    
    *Modify these in `.env` file*
    """)

    section("Recent System Events")
    from database import SessionLocal, SystemEvent
    db = SessionLocal()
    try:
        sys_events = db.query(SystemEvent).order_by(SystemEvent.timestamp.desc()).limit(20).all()
        if sys_events:
            sys_df = pd.DataFrame([{
                "Time": e.timestamp, "Component": e.component,
                "Type": e.event_type, "Status": e.status,
                "Message": (e.message or "")[:80],
            } for e in sys_events])
            st.dataframe(sys_df, use_container_width=True)
        else:
            empty_state("No system events logged yet.")
    finally:
        db.close()


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:0.75rem;color:#57606a;border-top:1px solid #e5e7eb;padding-top:0.5rem'>"
    "FinSakhi Admin Dashboard | Powered by IBM Granite | All metrics sourced from real execution data"
    "</div>",
    unsafe_allow_html=True,
)
