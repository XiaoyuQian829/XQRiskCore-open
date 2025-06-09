# core/context_injection.py

import streamlit as st
from utils.config_loader import load_client_registry
from core.client_context import ClientContext
from core.request_context import RequestContext  # for type hinting

def get_client_context_selector(ctx: "RequestContext") -> ClientContext:
    """
    Render the Sidebar client selector and return the bound ClientContext instance.
    - Admin users can view all clients
    - Other users are restricted to their assigned_clients only
    """
    registry = load_client_registry()
    all_clients = list(registry.keys())

    if ctx.role == "admin":
        available_clients = all_clients
    else:
        available_clients = getattr(ctx, "assigned_clients", []) or []

    print(f"[DEBUG] ctx.role = {ctx.role}")
    print(f"[DEBUG] ctx.assigned_clients = {getattr(ctx, 'assigned_clients', None)}")
    print(f"[DEBUG] client_registry keys = {all_clients}")
    print(f"[DEBUG] available_clients = {available_clients}")

    if not available_clients:
        st.sidebar.error("❌ No client available for your role.")
        st.stop()

    default_idx = available_clients.index(ctx.client_id) if ctx.client_id in available_clients else 0

    selected_id = st.sidebar.selectbox("🎯 Select Client", available_clients, index=default_idx, key="client_selector")
    return ClientContext(selected_id)