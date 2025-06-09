# frontend/roles/quant_researcher/dashabord.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Quant Research Console", sidebar_key="quant_sidebar")
    except Exception as e:
        st.error("❌ Quant dashboard failed to load.")
        st.exception(e)




