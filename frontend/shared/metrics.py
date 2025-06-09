# frontend/shared/metrics.py
"""
System Metrics and Cache
- Stores global system-level states
"""
from datetime import datetime
import streamlit as st

def init_system_metrics():
    """Initialize system-level runtime metrics."""
    if "system_metrics" not in st.session_state:
        st.session_state["system_metrics"] = {
            "startup_time": datetime.now(),
            "last_update": None,
            "total_trades": 0,
            "total_views": 0,
            "active_users": set(),
            "module_views": {}  # e.g. {"trade_form": 5}
        }

def get_metrics():
    """Return the current system metrics dict."""
    init_system_metrics()
    return st.session_state["system_metrics"]

def increment_trade_count():
    """Increase total trade count."""
    metrics = get_metrics()
    metrics["total_trades"] += 1
    metrics["last_update"] = datetime.now()

def increment_module_view(module: str):
    """Track how many times a module was viewed."""
    metrics = get_metrics()
    metrics["module_views"][module] = metrics["module_views"].get(module, 0) + 1
    metrics["total_views"] += 1
    metrics["last_update"] = datetime.now()

def register_user(user_id: str):
    """Track which users are active in this session."""
    metrics = get_metrics()
    metrics["active_users"].add(user_id)
