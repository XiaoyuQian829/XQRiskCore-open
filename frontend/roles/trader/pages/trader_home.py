
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
    Trader Welcome Panel
    ---------------------
    Entry overview for manual traders. Provides access to current portfolio view,
    trade submission tools, and approval status tracking.
    """

    st.markdown("""
        <h2 style='margin-bottom: 0.2rem;'>👋 Welcome, <span style='color: #3399ff;'>Manual Trader</span></h2>
        <div style='font-size: 0.95rem; margin-bottom: 1.2rem; color: #666;'>
            You are logged in as: <code><strong>{}</strong></code><br>
            Role: <strong>TRADER</strong><br>
            Access Level: Trade submission, portfolio review, and signal tracking.
        </div>
    """.format(ctx.user_id), unsafe_allow_html=True)

    # === Quick Access Overview ===
    st.markdown("### 📊 Portfolio & Trade Tools")
    st.markdown("Use the sidebar labels to access each module. Below are example actions to try:")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **📈 Portfolio Overview**  
        View your current holdings, exposure, drawdown, and unrealized P&L.  
        *Check asset breakdowns and risk flags.*  
        👉 Sidebar: `Trader: Portfolio Overview`

        **📝 Manual Trade Submit**  
        Submit a buy/sell intent for approval.  
        *Try buying 10 shares of AAPL and observe the risk signals.*  
        👉 Sidebar: `Trader: Manual Trade Submit`
        """)

    with col2:
        st.markdown("""
        **📬 Approval Status Tracker**  
        Track the status of submitted trades.  
        *Watch for 'approved', 'rejected', or 'cooling-off' states.*  
        👉 Sidebar: `Trader: Approval Status Tracker`
        """)

    # === Policy Reminder ===
    st.divider()
    st.info("""
    📌 **Reminder:**
    - All trade submissions are subject to pre-trade risk approval
    - Each submission generates a full audit record
    - Your trades may be blocked by cooling-off, kill-switch, or max drawdown limits
    """)

    # === Footer ===
    st.caption(f"🕒 Server Time: {get_timestamps()['ny_time_str']} (NYC)")
    st.caption("XQRiskCore v1.0 · Trader Interface Console (Beta)")
