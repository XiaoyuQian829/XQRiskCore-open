# frontend/roles/auditor/pages/auditor_home.py

REQUIRES_CLIENT_CONTEXT = False

import streamlit as st
from core.request_context import RequestContext
from utils.time_utils import get_timestamps
from users.user_registry import load_user_registry
from utils.config_loader import load_client_registry
from audit.action_logger import record_user_action
from utils.user_action import UserAction


def render(ctx: RequestContext):
    """
    Auditor Welcome Panel
    ---------------------
    Oversight console for auditors. Enables access to intent tracking, 
    decision logs, and event scan reviews for regulatory audit readiness.
    """

    st.markdown("""
        <h2 style='margin-bottom: 0.2rem;'>👋 Welcome, <span style='color: #cc6600;'>Auditor</span></h2>
        <div style='font-size: 0.95rem; margin-bottom: 1.2rem; color: #666;'>
            You are logged in as: <code><strong>{}</strong></code><br>
            Role: <strong>AUDITOR</strong><br>
            Access Level: Full audit trail visibility with read-only permissions.
        </div>
    """.format(ctx.user_id), unsafe_allow_html=True)

    st.markdown("### 🔍 Audit Trail Modules")
    st.markdown("Access complete logs and traceability records across risk and trading events.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🧭 Intent Trace Viewer**  
        Follow full lifecycle of submitted trades.  
        *Try reviewing how a rejected intent propagated through risk checks.*  
        👉 Sidebar: `Audit: Intent Trace Viewer`

        **📑 Decision Records**  
        View all trade approvals and rejections with justifications.  
        *Use filters to isolate high-risk overrides.*  
        👉 Sidebar: `Audit: Decision Records`
        """)

    with col2:
        st.markdown("""
        **📉 Trigger Event Logs**  
        Review what triggered automated safeguards.  
        *Look into which assets repeatedly triggered kill switches.*  
        👉 Sidebar: `Audit: Trigger Event Logs`

        **📆 Daily Oversight Sheet**  
        Snapshot of account status at end-of-day.  
        *Check which accounts were in silent or breached state.*  
        👉 Sidebar: `Audit: Daily Oversight Sheet`

        **📅 Periodic Scan Logs**  
        Inspect logs from scheduled system scans.  
        *Use this for quarterly compliance reporting.*  
        👉 Sidebar: `Audit: Periodic Scan Logs`
        """)

    st.divider()
    st.info("""
    📌 **Your audit panel supports governance transparency:**
    - All actions are tracked and timestamped
    - Role-based permissions ensure integrity
    - Logs are exportable for internal and external audits
    """)

    st.caption(f"🕒 Server Time: {get_timestamps()['ny_time_str']} (NYC)")
    st.caption("XQRiskCore v1.0 · Auditor Console (Beta)")
