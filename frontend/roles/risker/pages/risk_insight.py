# frontend/roles/risker/pages/risk_insight.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from glob import glob
from datetime import datetime

from core.client_context import ClientContext
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_view, record_user_action

# === 加载审计记录 ===
def load_json_or_jsonl(filepath):
    if filepath.endswith(".jsonl"):
        with open(filepath, "r") as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
    elif filepath.endswith(".json"):
        with open(filepath, "r") as f:
            return [json.load(f)]
    return []

# === 提取摘要字段 ===
def summarize_record(record):
    intent = record.get("intent", {})
    approval = record.get("approval", {})
    signals = approval.get("signals", {})
    ts = intent.get("timestamp")
    date = ts.split("T")[0] if isinstance(ts, str) and "T" in ts else ""

    return {
        "Date": date,
        "Symbol": intent.get("symbol"),
        "Score": approval.get("score"),
        "VAR": signals.get("var"),
        "CVAR": signals.get("cvar"),
        "Volatility": signals.get("volatility"),
        "Approved": approval.get("approved"),
        "Raw": record
    }

# === 主渲染入口 ===
def render(ctx: RequestContext, client: ClientContext):
    if not ctx.has_permission("risker.view_risk_insight"):
        st.warning("🚫 You do not have permission to view risk insights.")
        return

    # ✅ 页面访问行为日志
    record_user_view(ctx, module="risk_insight", action=UserAction.VIEW_RISK_INSIGHT)

    st.markdown("""
        <h3 style='font-size: 1.4rem;'>📈 Risk Insight & Historical Signals</h3>
        <div style='font-size: 0.9rem; color: #888;'>
            Visualize approval scores, risk indicators (VAR, CVAR, Volatility), and flag alerts from historical trade intents.
        </div>
    """, unsafe_allow_html=True)

    audit_path = os.path.join(client.base_path, "audit/decisions")
    files = sorted(glob(f"{audit_path}/*.json*"))

    rows = []
    for f in files:
        for r in load_json_or_jsonl(f):
            rows.append(summarize_record(r))

    df = pd.DataFrame(rows)
    df = df[df["Date"].notnull()].copy()
    df["Date"] = pd.to_datetime(df["Date"])

    # === 筛选器 ===
    symbols = sorted(df["Symbol"].dropna().unique())
    selected = st.multiselect("Filter by Symbol", symbols, default=symbols)

    df = df[df["Symbol"].isin(selected)]

    # ✅ 行为日志：筛选了哪些 symbol
    record_user_view(ctx, module="risk_insight", action="filter_symbols", payload={"symbols": selected})

    # === 概览表格 ===
    st.markdown("### 🧾 Summary Table (Latest per Symbol)")
    if not df.empty:
        latest_df = df.sort_values("Date").drop_duplicates("Symbol", keep="last")
        st.dataframe(latest_df[["Symbol", "Score", "VAR", "CVAR", "Volatility", "Approved"]], use_container_width=True)

    # === 趋势图 ===
    st.markdown("---")
    st.markdown("### 📊 Risk Indicator Trends")
    df = df.sort_values("Date").drop_duplicates(["Date", "Symbol"], keep="last")

    for col in ["Score", "VAR", "CVAR", "Volatility"]:
        st.markdown(f"#### {col} Over Time")
        fig = px.line(df, x="Date", y=col, color="Symbol", markers=True)

        if col == "VAR":
            warn_df = df[df["VAR"] < -0.05]
            for s in warn_df["Symbol"].unique():
                subset = warn_df[warn_df["Symbol"] == s]
                fig.add_scatter(x=subset["Date"], y=subset["VAR"], mode="markers", name=f"⚠️ High VAR {s}", marker=dict(size=10, color="red"))

        if col == "Score":
            reject_df = df[df["Approved"] == False]
            for s in reject_df["Symbol"].unique():
                subset = reject_df[reject_df["Symbol"] == s]
                fig.add_scatter(x=subset["Date"], y=subset["Score"], mode="markers", name=f"❌ Rejected {s}", marker=dict(size=10, color="orange"))

        st.plotly_chart(fig, use_container_width=True)

    # === 异常详情 ===
    st.markdown("---")
    st.markdown("### 🔍 Alert Detail Viewer")
    alerts = df[(df["VAR"] < -0.05) | (df["Approved"] == False)]
    for _, row in alerts.iterrows():
        label = f"{row['Symbol']} | {row['Date'].strftime('%Y-%m-%d')} | Score: {row['Score']:.3f} | VAR: {row['VAR']:.3f}"
        with st.expander(label):
            st.json(row["Raw"])

    # === 导出按钮（含行为日志） ===
    st.markdown("---")
    st.markdown("### 📥 Download Filtered Records")
    if st.download_button("Download CSV", data=df.to_csv(index=False), file_name="risk_insight_export.csv"):
        record_user_action(ctx, module="risk_insight", action="download_csv", payload={
            "filtered_symbols": selected,
            "record_count": len(df)
        })



