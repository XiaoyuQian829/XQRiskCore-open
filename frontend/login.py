# frontend/login.py

import streamlit as st
import time
import os
import sys
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from users.user_registry import load_user_registry
from core.request_context import build_request_context
from audit.action_logger import record_user_action
from utils.user_action import UserAction
from utils.avatar_loader import get_user_avatar_base64

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME_SECONDS = 60

@st.cache_data
def load_base64_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_logo():
    logo_path = "frontend/assets/xqrisk_logo.png"
    if os.path.exists(logo_path):
        logo64 = load_base64_image(logo_path)
        st.markdown(f"""
            <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
                <img src="data:image/png;base64,{logo64}" style="max-width: 300px;" />
            </div>
        """, unsafe_allow_html=True)

def render_avatar_block(selected_user, user_config):
    avatar_b64 = get_user_avatar_base64(selected_user)
    st.markdown(f'''
        <div style="text-align: center; margin-top: 10px; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{avatar_b64}" style="max-width: 112px; border-radius: 50%;" />
            <div style="margin-top: 4px; display: flex; justify-content: center; align-items: center; gap: 6px;">
                <span style="font-weight: 600; font-size: 1.2rem; color: white;">{selected_user}</span>
                <code style="font-size: 0.75rem; background-color: #111; color: #00ff88; padding: 2px 6px; border-radius: 4px;">
                    {user_config['role'].upper()}
                </code>
            </div>
        </div>
    ''', unsafe_allow_html=True)

def login_page():
    users = load_user_registry()
    priority_users = [
        "admin", "trader1", "risker", "auditor", "reporter",
        "strategy_agent", "compliance_officer", "quant_researcher"
    ]
    usernames = [u for u in priority_users if u in users] + sorted([u for u in users if u not in priority_users])

    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
        st.session_state.last_failed_time = 0

    if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
        elapsed = time.time() - st.session_state.last_failed_time
        if elapsed < LOCKOUT_TIME_SECONDS:
            st.error(f"⛔ Too many failed attempts. Wait {int(LOCKOUT_TIME_SECONDS - elapsed)} seconds.")
            return
        else:
            st.session_state.login_attempts = 0

    # === 居中列布局 ===
    cols = st.columns([1, 1, 1])
    with cols[1]:
        render_logo()

        selected_user = st.selectbox("👤 Select User", usernames)
        user_config = users[selected_user]
        render_avatar_block(selected_user, user_config)

        remembered_user = st.session_state.get("remembered_user")
        remembered_pwd = st.session_state.get("remembered_password", "")
        initial_pwd = user_config.get("password", "")
        if remembered_user == selected_user and remembered_pwd:
            initial_pwd = remembered_pwd

        with st.form("login_form"):
            password = st.text_input("🔑 Password", type="password", value=initial_pwd)
            remember = st.checkbox("Remember me", value=(remembered_user == selected_user))
            submitted = st.form_submit_button("Login")
    
        st.markdown("</div>", unsafe_allow_html=True)
        
        if submitted:
            if password == user_config.get("password"):
                if not user_config.get("active", True):
                    st.error("❌ This account has been deactivated.")
                    return
                st.session_state["authenticated"] = True
                st.session_state["request_ctx"] = build_request_context(selected_user)
                record_user_action(st.session_state["request_ctx"], module="login_page", action=UserAction.LOGIN)
                if remember:
                    st.session_state["remembered_user"] = selected_user
                    st.session_state["remembered_password"] = password
                else:
                    st.session_state.pop("remembered_user", None)
                    st.session_state.pop("remembered_password", None)
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.session_state.last_failed_time = time.time()
                st.error("❌ Incorrect password.")

