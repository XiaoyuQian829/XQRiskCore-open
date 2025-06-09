# frontend/roles/admin/pages/admin_home.py 

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
    Admin Welcome Panel
    -------------------
    Entry overview for system administrators. Includes role summary, system metrics,
    governance modules, and audit policies.
    """

    st.markdown("""
        <h2 style='margin-bottom: 0.2rem;'>👋 Welcome, <span style='color: #3399ff;'>System Administrator</span></h2>
        <div style='font-size: 0.95rem; margin-bottom: 1.2rem; color: #666;'>
            You are logged in as: <code><strong>{}</strong></code><br>
            Role: <strong>ADMIN</strong><br>
            Access Level: Full system governance, permissions, and client setup.
        </div>
    """.format(ctx.user_id), unsafe_allow_html=True)

    record_user_action(ctx, module="admin_home", action=UserAction.VIEW_MODULE)

    # === System Metrics Summary Table ===
    users = load_user_registry()
    clients = load_client_registry()
    risk_rules_count = 6  # Placeholder

    summary_data = {
        "Metric": ["👥 Users Registered", "🏦 Clients Onboarded", "🔒 Risk Rules Enabled"],
        "Value": [len(users), len(clients), risk_rules_count]
    }
    st.markdown("### 📊 System Overview")
    st.table(summary_data)

    # === Functional Modules Grid ===
    st.markdown("### 🧭 Governance Modules")
    st.markdown("Use the sidebar labels to access each module. Below are example use cases to explore:")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🔐 User & Role Manager**  
        Manage user lifecycle and role assignments.  
        *Try adding an `analyst` user and assigning read-only permissions.*  
        👉 Sidebar: `Admin: User & Role Manager`

        **🗂️ Client Registry Config**  
        Register clients and initialize portfolios.  
        *Try creating a mock client with dry run enabled.*  
        👉 Sidebar: `Admin: Client Registry Config`

        **✅ Role Permission Matrix**  
        Configure access rules using RBAC.  
        *Toggle permissions for `trader` and observe page access changes.*  
        👉 Sidebar: `Admin: Role Permission Matrix`
        """)

    with col2:
        st.markdown("""
        **📦 Tradable Asset Config**  
        Define asset universe and categories.  
        *Add a new ETF or bond to the tradable list.*  
        👉 Sidebar: `Admin: Tradable Asset Config`

        **🔧 Runtime Control Panel**  
        Manually trigger or release silent mode / kill switch.  
        *Click buttons to test portfolio-level protections.*  
        👉 Sidebar: `Admin: Runtime Control Panel`

        **🧾 User Action Logs**  
        Review structured logs for user/system activity.  
        *Filter by module or user ID to trace workflows.*  
        👉 Sidebar: `Admin: User Action Logs`
        """)

    st.markdown("""
        **⏱️ Intraday Trigger Rules**  
        Configure per-client trigger intervals.  
        *Temporarily disable scanning for test clients.*  
        👉 Sidebar: `Admin: Intraday Trigger Rules`
    """)

    # === Policy Reminder ===
    st.divider()
    st.info("""
    📌 **This platform enforces strict governance:**
    - All user actions are recorded and auditable
    - All configuration changes are permission-controlled
    - All trade intents require independent approval
    """)

    # === Footer ===
    st.caption(f"🕒 Server Time: {get_timestamps()['ny_time_str']} (NYC)")
    st.caption("XQRiskCore v1.0 · Risk Governance Console (Beta)")

