# frontend/roles/risker/pages/approval_panel.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
import os
import json
import pandas as pd
from glob import glob

from core.client_context import ClientContext
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_view, record_user_action

def load_json_or_jsonl(filepath):
    if filepath.endswith(".jsonl"):
        with open(filepath, "r") as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
    elif filepath.endswith(".json"):
        with open(filepath, "r") as f:
            return [json.load(f)]
    return []

def summarize_record(record):
    intent = record.get("intent", {})
    approval = record.get("approval", {})
    execution = record.get("execution", {})
    signals = approval.get("signals", {})

    return {
        "Intent ID": intent.get("intent_id"),
        "Symbol": intent.get("symbol"),
        "Action": intent.get("action"),
        "Score": approval.get("score"),
        "Approved": approval.get("approved"),
        "Regime": signals.get("regime"),
        "VaR": signals.get("var"),
        "CVaR": signals.get("cvar"),
        "Volatility": signals.get("volatility"),
        "Slippage %": execution.get("slippage_pct"),
        "Latency (ms)": execution.get("execution_latency_ms"),
        "Timestamp": intent.get("timestamp")
    }

def render(ctx: RequestContext, client: ClientContext):
    if not ctx.has_permission("risker.approve_trade"):
        st.warning("🚫 You do not have permission to review trade approvals.")
        return

    record_user_view(ctx, module="approval_panel", action=UserAction.VIEW_APPROVAL_PANEL)

    st.markdown("""
        <h3 style='font-size: 1.7rem;'>📄 Trade Approval Tracker</h3>
        <div style='font-size: 0.9rem; color: #888;'>
            Below are recent trade intents that are either high-risk or not approved. You may use this panel to initiate further review or download them for audit purposes.
        </div>
    """, unsafe_allow_html=True)

    audit_folder = os.path.join(client.base_path, "audit/decisions")
    files = sorted(glob(f"{audit_folder}/*.json*"), reverse=True)[:5]

    all_rows = []
    for f in files:
        records = load_json_or_jsonl(f)
        for r in records:
            all_rows.append(summarize_record(r))

    if not all_rows:
        st.info("🟡 No approval records found in recent files.")
        return

    df = pd.DataFrame(all_rows)

    flagged = df[(df["Approved"] == False) | (df["Score"] < -0.3)]

    record_user_view(ctx, module="approval_panel", action="filter_flagged_intents", payload={
        "total_records": len(df),
        "flagged_count": len(flagged)
    })

    st.markdown("### 🔍 Flagged Intents (Unapproved or Low Score)")

    if not flagged.empty:
        st.dataframe(flagged, use_container_width=True)

        if st.download_button(
            label="📥 Download CSV",
            data=flagged.to_csv(index=False),
            file_name="risker_review.csv",
            mime="text/csv"
        ):
            record_user_action(ctx, module="approval_panel", action="download_flagged_csv", payload={
                "record_count": len(flagged),
                "file": "risker_review.csv"
            })
    else:
        st.success("✅ All recent intents are approved and scored safely.")

