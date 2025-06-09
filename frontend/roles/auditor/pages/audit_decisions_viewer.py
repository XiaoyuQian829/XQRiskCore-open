# frontend/roles/auditor/pages/audit_decisions_viewer.py

REQUIRES_CLIENT_CONTEXT = True

import os, json
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from utils.time_utils import get_timestamps
from audit.action_logger import record_user_view, record_user_action
from core.client_context import ClientContext
from core.request_context import RequestContext
from utils.user_action import UserAction

DECISION_PATH = "audit/decisions"

def load_json_or_jsonl(filepath):
    try:
        if filepath.endswith(".jsonl"):
            with open(filepath, "r") as f:
                return [json.loads(line.strip()) for line in f if line.strip()]
        elif filepath.endswith(".json"):
            with open(filepath, "r") as f:
                return [json.load(f)]
    except Exception as e:
        print(f"[⚠️] Failed to load {filepath}: {e}")
    return []

def summarize_record(r):
    intent = r.get("intent", {})
    approval = r.get("approval", {})
    return {
        "Symbol": intent.get("symbol", "—"),
        "Action": intent.get("action", "—"),
        "Score": approval.get("score", "?"),
        "Approved": approval.get("approved", False),
        "Timestamp": intent.get("timestamp", "—"),
        "Raw": r
    }

def render(ctx: RequestContext, client: ClientContext):

    if not ctx.has_permission("auditor.view_audit_decisions"):
        st.warning("⚠️ You do not have permission to view audit decisions logs.")
        return

    record_user_view(ctx, module="audit_decisions", action=UserAction.VIEW_AUDIT_DECISIONS)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>🧠 Audit · Decision Logs</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            View and filter risk decision approvals by symbol, score threshold, and approval status.
        </div>
    """, unsafe_allow_html=True)

    base_path = os.path.join(client.base_path, DECISION_PATH)
    if not os.path.exists(base_path):
        st.warning("No audit/decisions directory found.")
        return

    # === Load records ===
    all_records = []
    for fname in sorted(os.listdir(base_path), reverse=True):
        if fname.endswith((".json", ".jsonl")):
            all_records.extend(load_json_or_jsonl(os.path.join(base_path, fname)))

    if not all_records:
        st.info("No decision audit records found.")
        return

    rows = [summarize_record(r) for r in all_records if isinstance(r, dict)]
    df = pd.DataFrame(rows)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Symbol", "Timestamp"]).sort_values("Timestamp")

    # === Symbol Selector ===
    symbols = sorted(df["Symbol"].dropna().unique())
    selected_symbol = st.selectbox("🔎 Select Symbol", symbols)
    sdf = df[df["Symbol"] == selected_symbol]

    record_user_view(ctx, module="audit_decisions", action="select_symbol", payload={"symbol": selected_symbol})

    # === Filtering Conditions ===
    st.markdown("### 🎯 Flagged Conditions")

    col1, col2 = st.columns(2)
    with col1:
        score_threshold = st.number_input("Score below", value=-0.3, step=0.05)
    with col2:
        only_unapproved = st.checkbox("Only show unapproved (❌)", value=False)

    record_user_view(ctx, module="audit_decisions", action="set_flagged_conditions", payload={
        "symbol": selected_symbol,
        "threshold": score_threshold,
        "only_unapproved": only_unapproved
    })

    sdf["Score"] = pd.to_numeric(sdf["Score"], errors="coerce")
    sdf["Approved"] = sdf["Approved"].fillna(False)
    mask = (sdf["Score"] < score_threshold) & (~sdf["Approved"] if only_unapproved else True)
    flagged = sdf[mask].copy()

    # === Flagged Summary ===
    if flagged.empty:
        st.success("✅ No flagged records based on current criteria.")
        return

    st.markdown(f"### 📊 {selected_symbol} · Score Trend")
    fig = px.line(sdf, x="Timestamp", y="Score", title="Approval Score", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧾 Flagged Records Table")
    st.dataframe(flagged[["Timestamp", "Action", "Score", "Approved"]], use_container_width=True)

    st.markdown("### 🔍 Flagged Record Details")
    for _, row in flagged.sort_values("Timestamp", ascending=False).head(5).iterrows():
        label = f"[{row['Timestamp'].strftime('%Y-%m-%d %H:%M')}] {row['Action']} | Score: {row['Score']} | {'✅' if row['Approved'] else '❌'}"
        with st.expander(label):
            record_user_action(ctx, module="audit_decisions", action="view_flagged_detail", payload={
                "symbol": row["Symbol"],
                "score": row["Score"]
            })
            st.json(row["Raw"])

    st.markdown("### 📥 Export Flagged Records")
    if st.download_button("Download CSV", data=flagged.to_csv(index=False), file_name=f"{selected_symbol}_flagged.csv"):
        record_user_action(ctx, module="audit_decisions", action="download_flagged_csv", payload={
            "symbol": selected_symbol,
            "threshold": score_threshold,
            "only_unapproved": only_unapproved,
            "count": len(flagged)
        })
