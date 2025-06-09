# frontend/roles/compliance_officer/dashabord.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Compliance Console", sidebar_key="compliance_sidebar")
    except Exception as e:
        st.error("❌ Compliance dashboard failed to load.")
        st.exception(e)
