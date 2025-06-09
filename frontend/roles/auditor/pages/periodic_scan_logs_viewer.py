# frontend/roles/auditor/pages/periodic_scan_logs_viewer.py

REQUIRES_CLIENT_CONTEXT = True

import os, json
import streamlit as st
import pandas as pd
from datetime import datetime

from core.client_context import ClientContext
from core.request_context import RequestContext
from audit.action_logger import record_user_view, record_user_action
from utils.user_action import UserAction

SCAN_PATH = "audit/periodic_scan_logs"

def load_jsonl(filepath):
    try:
        with open(filepath, "r") as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
    except Exception as e:
        print(f"[⚠️] Failed to load {filepath}: {e}")
        return []

def extract_summary(record):
    return {
        "Timestamp": record.get("scan_time") or record.get("timestamp"),
        "Symbol": record.get("symbol"),
        "Score": record.get("score"),
        "VAR": record.get("var"),
        "Volatility": record.get("volatility"),
        "Triggered": record.get("triggered", False),
        "Trigger Reason": record.get("reason") or record.get("trigger_reason", "-"),
        "Raw": record
    }

def render(ctx: RequestContext, client: ClientContext):

    if not ctx.has_permission("auditor.view_periodic_scan_logs"):
        st.warning("❌ You do not have permission to view periodic scan logs.")
        return

    record_user_view(ctx, module="periodic_scan_logs", action=UserAction.VIEW_PERIODIC_SCAN_LOGS)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>📡 Periodic Risk Scan Logs</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            View time-based scan results across your portfolio. Triggered assets, scores, VaR and volatility flags are listed with reasoning.
        </div>
    """, unsafe_allow_html=True)

    base_path = os.path.join(client.base_path, SCAN_PATH)
    if not os.path.exists(base_path):
        st.warning("No audit/periodic_scan_logs directory found.")
        return

    files = sorted([f for f in os.listdir(base_path) if f.endswith(".jsonl")], reverse=True)
    if not files:
        st.info("No scan log files found.")
        return

    max_files = st.slider("📂 Number of scans to display", 1, 20, 5)
    selected_files = files[:max_files]

    for fname in selected_files:
        full_path = os.path.join(base_path, fname)
        records = load_jsonl(full_path)
        rows = [extract_summary(r) for r in records if isinstance(r, dict)]
        if not rows:
            continue

        df = pd.DataFrame(rows)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = df.dropna(subset=["Timestamp"])

        scan_time_str = df["Timestamp"].max().strftime("%Y-%m-%d %H:%M:%S")
        flagged = df[df["Triggered"] == True]
        label = f"📄 {fname} | 🕒 {scan_time_str} | ⚠️ {len(flagged)} triggered"

        with st.expander(label):
            st.dataframe(
                df[["Symbol", "Score", "VAR", "Volatility", "Triggered", "Trigger Reason"]],
                use_container_width=True
            )

            if not flagged.empty:
                st.markdown("### 🔍 Triggered Assets (Expanded)")
                for _, row in flagged.iterrows():
                    sublabel = f"{row['Symbol']} | Score: {row['Score']} | VAR: {row['VAR']}"
                    with st.expander(sublabel):
                        record_user_action(ctx, module="periodic_scan_logs", action="view_trigger_detail", payload={
                            "symbol": row["Symbol"],
                            "score": row["Score"]
                        })
                        st.json(row["Raw"])
            else:
                st.success("✅ No assets were triggered in this scan.")

            st.markdown("### 📥 Export Full Scan")
            if st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name=f"scan_{fname.replace('.jsonl','')}.csv"
            ):
                record_user_action(ctx, module="periodic_scan_logs", action="download_csv", payload={
                    "file": fname,
                    "count": len(df)
                })
