# frontend/roles/compliance_officer/pages/manual_override_log.py

import streamlit as st
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action

REQUIRES_CLIENT_CONTEXT = False

def render(ctx: RequestContext):
    if not ctx.has_permission("compliance_officer.view_overrides"):
        st.warning("You do not have permission to view override records.")
        return

    record_user_action(ctx, module="manual_override_log", action=UserAction.VIEW_MANUAL_OVERRIDES)

    st.markdown("### 🛠️ Manual Override Tracker")
    st.info("This view will summarize all manual risk overrides and related audit trails.")
