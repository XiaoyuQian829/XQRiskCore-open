# frontend/shared/dashboard_template.py

import streamlit as st
from core.request_context import RequestContext
from core.context_injection import get_client_context_selector
from audit.action_logger import record_user_action
from utils.user_action import UserAction
from frontend.page_registry.role_page_map import get_visible_pages


def render_role_dashboard(ctx: RequestContext, role_label: str, sidebar_key: str = "sidebar_nav"):
    """
    render_role_dashboard
    =====================
    Universal renderer for any role-based dashboard page.
    
    Parameters:
    - ctx: current RequestContext (includes user ID, role, permissions, etc.)
    - role_label: string to display in sidebar (e.g., "Admin Console")
    - sidebar_key: unique key for Streamlit radio (to isolate session state)
    """

    # === Sidebar header ===
    st.sidebar.subheader(role_label)

    # === Log that the user entered this dashboard ===
    record_user_action(ctx, module=f"{ctx.role}_dashboard", action=UserAction.SWITCH_PAGE)

    # === Load visible pages for this user (across all roles if permissions allow) ===
    visible_pages = get_visible_pages(ctx)

    if not visible_pages:
        st.sidebar.error("🚫 No accessible modules.")
        return

    # === Sidebar page selector ===
    selected_label = st.sidebar.radio(
        label="",  # Hide label to keep sidebar clean
        options=list(visible_pages.keys()),
        index=0,
        key=sidebar_key,
        label_visibility="collapsed"
    )

    # === Get selected module + required permission ===
    perm, module = visible_pages[selected_label]

    # === Optional debugging: print permission check details ===
    if perm:
        st.toast(f"🔍 Checking permission: `{perm}`")
        print("🧾 [PERM CHECK] Selected page:", selected_label)
        print("🧾 [PERM CHECK] Required permission:", perm)
        print("🧾 [PERM CHECK] Current ctx.permissions:", ctx.permissions)
        print("🧾 [PERM CHECK] Has permission?", ctx.has_permission(perm))
        print("🧾 [PERM CHECK] All keys:", list(ctx.permissions.keys()))
        for key in ctx.permissions:
            print(f"→ KEY: {repr(key)} == {repr(perm)} ? →", key == perm)

        # === Enforce permission check ===
        if not ctx.has_permission(perm):
            st.error(f"🚫 Access denied: you lack permission `{perm}`")
            return

    # === Log this module view for auditing ===
    record_user_action(
        ctx,
        module=f"{ctx.role}_dashboard",
        action=UserAction.VIEW_MODULE,
        payload={"module": selected_label}
    )

    # === Inject client context if the module requires it ===
    if getattr(module, "REQUIRES_CLIENT_CONTEXT", False):
        client_ctx = get_client_context_selector(ctx)
        module.render(ctx, client_ctx)
    else:
        module.render(ctx)
