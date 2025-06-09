import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from layout.sidebar import render_sidebar
from layout.header import render_header
from core.request_context import RequestContext

def lazy_import_dashboard(role: str):
    if role == "admin":
        from frontend.roles.admin import dashboard as module
    elif role == "trader":
        from frontend.roles.trader import dashboard as module
    elif role == "risker":
        from frontend.roles.risker import dashboard as module
    elif role == "auditor":
        from frontend.roles.auditor import dashboard as module
    elif role == "reporter":
        from frontend.roles.reporter import dashboard as module
    elif role == "quant_researcher":
        from frontend.roles.quant_researcher import dashboard as module
    elif role == "compliance_officer":
        from frontend.roles.compliance_officer import dashboard as module
    elif role == "strategy_agent":
        from frontend.roles.strategy_agent import dashboard as module
    else:
        return None
    return module

def main_dashboard(ctx: RequestContext):
    render_header(ctx)
    render_sidebar(ctx)
    dashboard = lazy_import_dashboard(ctx.role)
    if dashboard:
        dashboard.render(ctx)
    else:
        st.warning(f"⚠️ Unknown role: {ctx.role}. No dashboard available.")
