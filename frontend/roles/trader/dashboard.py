# frontend/roles/trader/dashboard.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Trader Console", sidebar_key="trader_sidebar")
    except Exception as e:
        st.error("❌ Trader dashboard failed to load.")
        st.exception(e)
