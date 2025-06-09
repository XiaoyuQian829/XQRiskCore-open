# frontend/roles/admin/pages/action_log_viewer.py

REQUIRES_CLIENT_CONTEXT = False

import streamlit as st
import os
import json
import pandas as pd
import yaml
import io
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

LOG_BASE_PATH = "audit/user_action_logs"

def render(ctx: RequestContext):
    if not ctx.has_permission("admin.view_action_logs"):
        st.warning("You do not have permission to view user activity logs.")
        return

    record_user_view(ctx, module="action_log_viewer", action=UserAction.VIEW_ACTION_LOG)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.5rem;'>📜 User Action Log Viewer</h3>
        <div style='font-size: 0.9rem; color: #999;'>Trace user behavior for audit and diagnostics.</div>
    """, unsafe_allow_html=True)

    if not os.path.exists(LOG_BASE_PATH):
        st.error("Log directory not found.")
        return

    roles = sorted([r for r in os.listdir(LOG_BASE_PATH) if os.path.isdir(os.path.join(LOG_BASE_PATH, r))])
    selected_role = st.selectbox("Select Role", roles)

    user_base = os.path.join(LOG_BASE_PATH, selected_role)
    users = sorted([u for u in os.listdir(user_base) if os.path.isdir(os.path.join(user_base, u))])
    selected_user = st.selectbox("Select User", users)

    date_base = os.path.join(user_base, selected_user)
    dates = sorted([d for d in os.listdir(date_base) if os.path.isdir(os.path.join(date_base, d))])
    selected_date = st.selectbox("Select Date", dates)

    log_path = os.path.join(date_base, selected_date, "events.jsonl")
    st.code(log_path, language="bash")

    if not os.path.exists(log_path):
        st.warning("No log file found.")
        return

    with open(log_path, "r") as f:
        lines = f.readlines()

    if not lines:
        st.info("Log file is empty.")
        return

    record_user_action(ctx, module="action_log_viewer", action="open_log_file", payload={
        "target_role": selected_role,
        "target_user": selected_user,
        "date": selected_date,
        "path": log_path
    })

    parsed = []
    for line in lines:
        try:
            rec = json.loads(line.strip())
            parsed.append({
                "timestamp": rec.get("timestamp", "-"),
                "module": rec.get("module", "-"),
                "action": rec.get("action", "-"),
                "status": rec.get("status", "-"),
                "payload": rec.get("payload", {}),
                "payload_str": json.dumps(rec.get("payload", {}), ensure_ascii=False)
            })
        except Exception as e:
            parsed.append({
                "timestamp": "-",
                "module": "ParseError",
                "action": str(e),
                "status": "error",
                "payload": {},
                "payload_str": line.strip()
            })

    if not parsed:
        st.info("No valid entries parsed.")
        return

    df = pd.DataFrame(parsed)

    modules = sorted(df["module"].unique())
    selected_modules = st.multiselect("Filter by Module", modules, default=modules)
    filtered_df = df[df["module"].isin(selected_modules)]

    st.markdown("### Parsed Log Records")
    st.dataframe(filtered_df[["timestamp", "module", "action", "status", "payload_str"]], use_container_width=True)

    export_json = json.dumps(filtered_df.drop(columns=["payload_str"]).to_dict(orient="records"), indent=2, ensure_ascii=False)
    export_yaml = yaml.dump(json.loads(export_json), sort_keys=False, allow_unicode=True)

    col1, col2 = st.columns(2)
    col1.download_button(
        "⬇️ Export as JSON",
        data=export_json,
        file_name=f"{selected_user}_{selected_date}_logs.json",
        mime="application/json"
    )
    col2.download_button(
        "⬇️ Export as YAML",
        data=export_yaml,
        file_name=f"{selected_user}_{selected_date}_logs.yaml",
        mime="text/yaml"
    )

