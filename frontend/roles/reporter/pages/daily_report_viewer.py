# frontend/roles/reporter/pages/daily_report_viewer.py

import streamlit as st
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action

REQUIRES_CLIENT_CONTEXT = True

def render(ctx: RequestContext, client_ctx):
    if not ctx.has_permission("reporter.view_daily"):
        st.warning("You do not have permission to view daily reports.")
        return

    record_user_action(ctx, module="daily_report_viewer", action=UserAction.VIEW_DAILY_REPORT)

    st.markdown("### 📅 Daily Report Viewer")
    st.info("This module will display daily trading or risk reports for review.")
