# frontend/roles/admin/pages/intraday_trigger_control.py

REQUIRES_CLIENT_CONTEXT = False

import streamlit as st
import yaml
import io
import os
import json
from glob import glob
from datetime import datetime
from core.request_context import RequestContext
from utils.config_loader import load_client_registry, save_client_registry
from utils.time_utils import get_timestamps
from utils.user_action import UserAction
from audit.action_logger import record_user_view, record_user_action  # ✅ 双轨日志

def get_last_scan_timestamp(client_id: str) -> str:
    scan_dir = os.path.join("clients", client_id, "audit", "periodic_scan_logs")
    if not os.path.exists(scan_dir):
        return "—"
    logs = sorted(glob(os.path.join(scan_dir, "*.jsonl")), reverse=True)
    for fpath in logs:
        with open(fpath, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                try:
                    data = json.loads(lines[-1])
                    ts_str = data.get("timestamp")
                    if ts_str:
                        dt = datetime.fromisoformat(ts_str)
                        return dt.strftime("%b %d, %Y @ %H:%M:%S")
                except Exception:
                    continue
    return "—"

def render(ctx: RequestContext):
    if not ctx.has_permission("admin.intraday_trigger_control"):
        st.warning("⚠️ You do not have permission to control intraday trigger.")
        return

    # ✅ 页面进入日志
    record_user_view(ctx, module="intraday_trigger_control",action=UserAction.VIEW_INTRADAY_TRIGGER_SETTINGS)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>Intraday Trigger Settings</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            Enable or disable intraday risk scanning for each client and set their trigger interval (in minutes).
        </div>
    """, unsafe_allow_html=True)

    registry = load_client_registry()
    updated_registry = {}
    changes_made = False

    for client_id, info in registry.items():
        with st.expander(f"🧾 Client: `{client_id}`", expanded=False):
            last_scan = get_last_scan_timestamp(client_id)
            st.markdown(
                f"<div style='color: #888; font-size: 0.85rem;'>Last Scan: <strong>{last_scan}</strong></div>",
                unsafe_allow_html=True
            )

            enable = st.toggle(
                "Enable Intraday Trigger",
                value=info.get("enable_intraday_trigger", True),
                key=f"{client_id}__enable"
            )
            interval = st.slider(
                "Trigger Interval (minutes)",
                min_value=5,
                max_value=120,
                step=5,
                value=info.get("intraday_trigger_interval_minutes", 10),
                key=f"{client_id}__interval"
            )
            if enable != info.get("enable_intraday_trigger") or interval != info.get("intraday_trigger_interval_minutes"):
                info["enable_intraday_trigger"] = enable
                info["intraday_trigger_interval_minutes"] = interval
                updated_registry[client_id] = info
                changes_made = True

    st.divider()

    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        if st.button("💾 Save Changes", use_container_width=True) and changes_made:
            registry.update(updated_registry)
            save_client_registry(registry)

            # ✅ 行为日志
            record_user_action(ctx, module="intraday_trigger_control", action=UserAction.SAVE_TRIGGER_SETTINGS, payload=updated_registry)

            # ✅ 系统日志
            ctx.log_action("admin", "modify_intraday_trigger_settings", updated_registry)

            st.session_state["just_saved_intraday"] = True
            st.toast("✅ Trigger settings saved successfully.")

    with col2:
        with st.expander("📤 Export YAML"):
            yaml_export = yaml.dump(registry, sort_keys=False)
            st.download_button(
                "Download client_registry.yaml",
                data=io.BytesIO(yaml_export.encode()),
                file_name="client_registry.yaml",
                mime="text/yaml"
            )


