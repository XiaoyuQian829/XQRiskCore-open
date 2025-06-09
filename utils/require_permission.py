# utils/require_permission.py

import streamlit as st
from functools import wraps

def require_permission(permission_key: str, show_error: bool = True):
    """
    Page-level access control decorator.

    This decorator enforces Role-Based Access Control (RBAC) by checking whether
    the current user session (via `ctx`) has the required permission key.

    Args:
        permission_key (str): The permission string to check (e.g. "trader.view_portfolio").
        show_error (bool): Whether to display an error in the UI if access is denied.

    Usage:
        @require_permission("trader.view_portfolio")
        def render(ctx, client_ctx):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(ctx, *args, **kwargs):
            if not ctx.has_permission(permission_key):
                if show_error:
                    st.error(f"🚫 You do not have permission: `{permission_key}`")
                return  # Stop execution if no permission
            return func(ctx, *args, **kwargs)
        return wrapper
    return decorator
