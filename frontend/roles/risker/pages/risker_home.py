# frontend/roles/risker/pages/risker_home.py

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
    Risk Manager Welcome Panel
    --------------------------
    Overview for risk managers. Provides access to trade approval, 
    signal analytics, trigger logs, and runtime safeguard tools.
    """

    st.markdown("""
        <h2 style='margin-bottom: 0.2rem;'>👋 Welcome, <span style='color: #e85c33;'>Risk Manager</span></h2>
        <div style='font-size: 0.95rem; margin-bottom: 1.2rem; color: #666;'>
            You are logged in as: <code><strong>{}</strong></code><br>
            Role: <strong>RISKER</strong><br>
            Access Level: Trade approvals, signal evaluation, runtime control, and trigger audits.
        </div>
    """.format(ctx.user_id), unsafe_allow_html=True)

    st.markdown("### 🛡 Risk Oversight Modules")
    st.markdown("Explore tools for approving trades, reviewing risk signals, and triggering safeguards.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **✅ Trade Approval Panel**  
        Review and approve submitted trade intents.  
        *Try approving or rejecting a new trader submission.*  
        👉 Sidebar: `Risker: Trade Approval Panel`

        **📊 Risk Signal Dashboard**  
        Visualize scoring components like drawdown, VaR, exposure.  
        *Inspect how signals vary per asset and account.*  
        👉 Sidebar: `Risker: Risk Signal Dashboard`
        """)

    with col2:
        st.markdown("""
        **🛑 Runtime Safeguards**  
        Manually trigger Silent Mode or Kill Switch per account or asset.  
        *Try freezing an account to simulate breach handling.*  
        👉 Sidebar: `Risker: Runtime Safeguards`

        **📋 Trigger Scan History**  
        View logs from intraday and periodic risk scans.  
        *See what triggered alerts in recent sessions.*  
        👉 Sidebar: `Risker: Trigger Scan History`
        """)

    st.divider()
    st.info("""
    📌 **Your role enables pre-trade risk gating & real-time intervention:**
    - Approvals follow standardized signal scoring
    - Kill Switch can freeze accounts or assets at risk
    - All risk actions are traceable and timestamped
    """)

    st.caption(f"🕒 Server Time: {get_timestamps()['ny_time_str']} (NYC)")
    st.caption("XQRiskCore v1.0 · Risk Manager Console (Beta)")
