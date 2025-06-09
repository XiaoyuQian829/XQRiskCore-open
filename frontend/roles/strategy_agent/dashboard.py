# frontend/roles/strategy_agent/dashboard.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Strategy Agent Console", sidebar_key="strategy_sidebar")
    except Exception as e:
        st.error("❌ Strategy Agent dashboard failed to load.")
        st.exception(e)
