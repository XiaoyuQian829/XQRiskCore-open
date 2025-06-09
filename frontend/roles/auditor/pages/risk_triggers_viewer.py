# frontend/roles/auditor/pages/risk_triggers_viewer.py

REQUIRES_CLIENT_CONTEXT = True

import os, json
import streamlit as st
import pandas as pd
from datetime import datetime

from core.client_context import ClientContext
from core.request_context import RequestContext
from audit.action_logger import record_user_view, record_user_action
from utils.time_utils import get_timestamps
from utils.user_action import UserAction

TRIGGER_MODULES = {
    "killswitch_logs": "KillSwitch",
    "cooling_off_logs": "CoolingOff"
}

def load_json_or_jsonl(filepath):
    try:
        if filepath.endswith(".jsonl"):
            with open(filepath, "r") as f:
                return [json.loads(line.strip()) for line in f if line.strip()]
        elif filepath.endswith(".json"):
            with open(filepath, "r") as f:
                return [json.load(f)]
    except Exception as e:
        print(f"[⚠️] Failed to load {filepath}: {e}")
    return []

def extract_trigger_summary(record, source_module):
    asset = record.get("symbol") or record.get("asset")
    return {
        "Timestamp": record.get("timestamp") or record.get("time") or record.get("trigger_time"),
        "Symbol": str(asset),
        "TriggeredBy": record.get("user_id") or record.get("source", "system"),
        "Reason": record.get("reason", "—"),
        "TriggerType": TRIGGER_MODULES.get(source_module, source_module),
        "Days": record.get("days", record.get("duration", 0)),
        "Raw": record
    }

def render(ctx: RequestContext, client: ClientContext):

    if not ctx.has_permission("auditor.view_risk_triggers"):
        st.warning("❌ You do not have permission to view risk triggers.")
        return

    record_user_view(ctx, module="risk_triggers", action=UserAction.VIEW_RISK_TRIGGERS)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>🔒 Risk Trigger Logs</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            View and filter recorded KillSwitch and Cooling-Off triggers across the risk system.
        </div>
    """, unsafe_allow_html=True)

    base_path = client.base_path
    all_entries = []

    for folder, label in TRIGGER_MODULES.items():
        full_path = os.path.join(base_path, "audit", folder)
        if not os.path.exists(full_path):
            continue
        for fname in sorted(os.listdir(full_path), reverse=True):
            if fname.endswith((".json", ".jsonl")):
                for r in load_json_or_jsonl(os.path.join(full_path, fname)):
                    entry = extract_trigger_summary(r, folder)
                    entry["Module"] = folder
                    all_entries.append(entry)

    if not all_entries:
        st.info("No trigger logs found.")
        return

    df = pd.DataFrame(all_entries)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp", ascending=False)

    # === Filter Section ===
    st.markdown("### 🎯 Filters")
    cols = st.columns(3)
    with cols[0]:
        symbols = sorted(df["Symbol"].dropna().unique())
        selected_symbol = st.selectbox("Symbol", ["(All)"] + symbols)
    with cols[1]:
        types = sorted(df["TriggerType"].dropna().unique())
        selected_type = st.selectbox("Trigger Type", ["(All)"] + types)
    with cols[2]:
        users = sorted(df["TriggeredBy"].dropna().unique())
        selected_user = st.selectbox("Triggered By", ["(All)"] + users)

    filtered = df.copy()
    if selected_symbol != "(All)":
        filtered = filtered[filtered["Symbol"] == selected_symbol]
    if selected_type != "(All)":
        filtered = filtered[filtered["TriggerType"] == selected_type]
    if selected_user != "(All)":
        filtered = filtered[filtered["TriggeredBy"] == selected_user]

    record_user_view(ctx, module="risk_triggers", action="apply_filters", payload={
        "symbol": selected_symbol,
        "type": selected_type,
        "user": selected_user,
        "count": len(filtered)
    })

    # === Summary Table ===
    st.markdown("### 📋 Triggered Events")
    st.dataframe(
        filtered[["Timestamp", "Symbol", "TriggerType", "Reason", "Days", "TriggeredBy"]],
        use_container_width=True
    )

    # === Export CSV ===
    st.markdown("### 📥 Export")
    if st.download_button("Download CSV", data=filtered.to_csv(index=False), file_name="risk_triggers.csv"):
        record_user_action(ctx, module="risk_triggers", action="download_trigger_csv", payload={"count": len(filtered)})

    # === Expanded View ===
    st.markdown("### 🔍 Record Details")
    for _, row in filtered.head(5).iterrows():
        label = f"{row['Timestamp'].strftime('%Y-%m-%d %H:%M')} | {row['Symbol']} | {row['TriggerType']}"
        with st.expander(label):
            st.json(row["Raw"])
