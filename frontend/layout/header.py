# frontend/layout/header.py

import streamlit as st
from datetime import datetime
# Assuming core.request_context and utils.avatar_loader are available
from core.request_context import RequestContext # Placeholder import
from utils.avatar_loader import get_user_avatar_base64 # Placeholder import
import base64

def render_header(ctx: RequestContext):
    username = ctx.user_id
    role = ctx.role
    today = datetime.now().strftime("%Y-%m-%d")
    avatar_base64 = get_user_avatar_base64(username)
    avatar_bytes = base64.b64decode(avatar_base64)

    # Use a single row for title and user/logout info
    # The columns distribution might need tweaking based on actual content width
    title_col, user_info_col, logout_col = st.columns([10, 3, 1.5])

    with title_col:
        st.markdown("""
        <div class="header-title">
            <h2>XQRiskCore Risk Governance Console</h2>
        </div>
        """, unsafe_allow_html=True)

    with user_info_col:
        # User info group (avatar, username, role, date)
        # You might need to use nested columns or custom CSS for precise alignment
        user_info_col1, user_info_col2 = st.columns([3, 4])
        
        with user_info_col1:
            st.image(avatar_bytes, width=72)  # ✅ 放大头像尺寸（建议 80px）
        
        with user_info_col2:
            st.markdown(f"<div style='font-weight:600; font-size:14px; color:white;'><strong>User:</strong> {username}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:600; font-size:14px; color:#1E90FF;'><strong>Role:</strong> {role}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#ccc; font-size:13px;'>📅 <strong>Date:</strong> {today}</div>", unsafe_allow_html=True)



    with logout_col:
        # Adjust button alignment with custom CSS if needed
        st.write("") # Add a small space for alignment if required
        if st.button("Logout", key="trigger_logout_dialog_opt1"):
            st.session_state["show_logout_dialog"] = True

    # --- Logout Confirmation (remains largely the same) ---
    if st.session_state.get("show_logout_dialog", False):
        st.warning(f"Are you sure you want to logout, **{username}**?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Logout", key="confirm_logout_opt1"):
                # Placeholder for actual action logger and session clear
                # from audit.action_logger import record_user_action
                # from utils.user_action import UserAction
                # record_user_action(ctx, module="header", action=UserAction.LOGOUT)
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_logout_opt1"):
                st.session_state["show_logout_dialog"] = False

    # === Divider Line ===
    st.markdown("<hr>", unsafe_allow_html=True)

# --- How to use (for testing) ---
# st.session_state["user_ctx"] = RequestContext("test_user", "Admin") # Set a dummy context
# render_header_option1(st.session_state["user_ctx"])
