# frontend/roles/trader/pages/approval_status_viewer.py

REQUIRES_CLIENT_CONTEXT = True

import os
import json
import streamlit as st
from glob import glob

from core.request_context import RequestContext
from core.client_context import ClientContext
from utils.visualization import render_approval_status
from utils.user_action import UserAction
from audit.action_logger import record_user_view

def load_audit_records(base_path: str):
    audit_path = os.path.join(base_path, "audit", "decisions")
    files = sorted(glob(f"{audit_path}/*.json*"), reverse=True)[:10]
    records = []
    for f in files:
        with open(f, "r") as infile:
            lines = [line.strip() for line in infile if line.strip()]
            for line in lines:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

def render(ctx: RequestContext, client: ClientContext):
    if not ctx.has_permission("trader.view_approval_status"):
        st.warning("🚫 You do not have permission to view approval status.")
        return

    record_user_view(ctx, module="approval_status_viewer", action=UserAction.VIEW_APPROVAL_STATUS)

    st.markdown(f"""
    <div style='padding: 0.6rem 1rem; background-color: rgba(255,255,255,0.05); border-left: 4px solid #4dabf7; margin-bottom: 1rem; font-size: 0.95rem; color: #eee;'>
        🛡️ <strong style="color: #ccc;">Approval Status Viewer</strong> for <code style="background-color: rgba(255,255,255,0.08); color: #00e676;">{client.client_id}</code>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>📊 Recent Trade Approval Status</h3>
        <div style='font-size: 0.9rem; color: #bbb; margin-bottom: 1rem;'>
            View your latest manual trade submissions and their associated risk approval results.
        </div>
    """, unsafe_allow_html=True)

    all_records = load_audit_records(client.base_path)
    trader_id = ctx.user_id or "unknown"
    matched = [r for r in all_records if r.get("intent", {}).get("trader_id") == trader_id]

    if not matched:
        st.info("You have no recent trade audit records.")
        return

    for record in matched[:5]:
        intent = record.get("intent", {})
        approval = record.get("approval", {})

        record_user_view(ctx, module="approval_status_viewer", action=UserAction.VIEW_APPROVAL_STATUS, payload={
            "intent_id": intent.get("intent_id"),
            "symbol": intent.get("symbol"),
            "approved": approval.get("approved"),
            "score": approval.get("score")
        })

        render_approval_status(record)
