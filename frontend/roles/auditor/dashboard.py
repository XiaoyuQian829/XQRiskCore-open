# frontend/roles/auditor/dashboard.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st
import traceback

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Auditor Console", sidebar_key="auditor_sidebar")
    except Exception as e:
        st.error("❌ Auditor dashboard failed to load.")
        st.exception(e)
