# frontend/roles/reporter/dashabord.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Reporter Console", sidebar_key="reporter_sidebar")
    except Exception as e:
        st.error("❌ Reporter dashboard failed to load.")
        st.exception(e)  # 可在部署时改为 log_exception(ctx, e)
