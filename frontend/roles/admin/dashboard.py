# frontend/roles/admin/dashboard.py

from core.request_context import RequestContext
from frontend.shared.dashboard_template import render_role_dashboard
import streamlit as st
import traceback

def render(ctx: RequestContext):
    try:
        render_role_dashboard(ctx, role_label="Admin Console", sidebar_key="admin_sidebar")
    except Exception as e:
        st.error("❌ Admin dashboard failed to load. Please contact system admin.")
        st.exception(e)  # or log to audit trail
        # Optional: log traceback manually
        # log_exception(ctx, e)
