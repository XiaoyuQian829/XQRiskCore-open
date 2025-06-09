# frontend/roles/reporter/pages/attribution_breakdown.py

import streamlit as st
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action

REQUIRES_CLIENT_CONTEXT = True

def render(ctx: RequestContext, client_ctx):
    if not ctx.has_permission("reporter.view_attribution"):
        st.warning("You do not have permission to view attribution breakdown.")
        return

    record_user_action(ctx, module="attribution_breakdown", action=UserAction.VIEW_ATTRIBUTION_BREAKDOWN)

    st.markdown("### 🧮 Attribution Breakdown")
    st.info("This view will break down portfolio performance by asset, strategy, or risk factor.")
