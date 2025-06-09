# frontend/roles/auditor/pages/daily_summary_viewer.py

REQUIRES_CLIENT_CONTEXT = True

import os, json
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from core.client_context import ClientContext
from core.request_context import RequestContext
from audit.action_logger import record_user_view, record_user_action
from utils.user_action import UserAction

SUMMARY_PATH = "audit/daily_summary"

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[⚠️] Failed to load {path}: {e}")
        return None

def render(ctx: RequestContext, client: ClientContext):

    if not ctx.has_permission("auditor.view_daily_summary"):
        st.warning("⚠️ You do not have permission to view daily summary.")
        return

    record_user_view(ctx, module="daily_summary", action=UserAction.VIEW_DAILY_SUMMARY)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>📘 Daily Risk Summary</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            Review risk snapshots across recent trading days, including net value, drawdown, mode status, score distribution and reason trace.
        </div>
    """, unsafe_allow_html=True)

    base_path = os.path.join(client.base_path, SUMMARY_PATH)
    if not os.path.exists(base_path):
        st.warning("No audit/daily_summary directory found.")
        return

    files = sorted([
        f for f in os.listdir(base_path)
        if f.endswith(".json") and f[:10].count("-") == 2
    ], reverse=True)

    if not files:
        st.info("No summary files found.")
        return

    max_display = st.slider("📅 Number of days to display", 1, 15, 5)
    selected_files = files[:max_display]

    for fname in selected_files:
        fpath = os.path.join(base_path, fname)
        record = load_json(fpath)
        if not record:
            continue

        date_str = fname.replace(".json", "")
        net_value = record.get("net_value", "?")
        drawdown = record.get("drawdown_pct", "?")
        silent = "🟡 ON" if record.get("silent_mode", False) else "✅ OFF"
        kill = "🔴 ON" if record.get("killswitch", False) else "✅ OFF"
        score_avg = record.get("score_avg", "?")
        reason = record.get("reason_summary", "-")
        score_dist = record.get("score_distribution")

        with st.expander(f"📅 {date_str}  |  💰 Net: {net_value}  |  📉 DD: {drawdown}  |  😶 Silent: {silent}  |  ⛔ Kill: {kill}"):
            st.markdown(f"""
                <div style='font-size: 0.92rem;'>
                • <b>Net Value</b>: <code>{net_value}</code><br>
                • <b>Drawdown %</b>: <code>{drawdown}</code><br>
                • <b>Score Avg</b>: <code>{score_avg}</code><br>
                • <b>Silent Mode</b>: {silent}<br>
                • <b>Kill Switch</b>: {kill}<br>
                • <b>Reason Summary</b>: <code>{reason}</code>
                </div>
            """, unsafe_allow_html=True)

            record_user_action(ctx, module="daily_summary", action="view_summary_detail", payload={
                "date": date_str,
                "net": net_value,
                "dd": drawdown,
                "silent": silent,
                "kill": kill
            })

            if isinstance(score_dist, dict) and len(score_dist) > 0:
                dist_df = pd.DataFrame({
                    "Score Bin": list(score_dist.keys()),
                    "Count": list(score_dist.values())
                })
                dist_df["Score Bin"] = pd.Categorical(dist_df["Score Bin"], ordered=True, categories=dist_df["Score Bin"])
                fig = px.bar(dist_df, x="Score Bin", y="Count", title="Score Distribution", text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(record, indent=2),
                file_name=fname
            )

