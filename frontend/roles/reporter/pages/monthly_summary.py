# frontend/roles/reporter/pages/monthly_summary.py

import streamlit as st
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action

REQUIRES_CLIENT_CONTEXT = True

def render(ctx: RequestContext, client_ctx):
    if not ctx.has_permission("reporter.view_monthly"):
        st.warning("You do not have permission to view monthly summaries.")
        return

    record_user_action(ctx, module="monthly_summary", action=UserAction.VIEW_MONTHLY_SUMMARY)

    st.markdown("### 📆 Monthly Summary")
    st.info("This module will summarize monthly performance, exposure, and drawdowns.")
