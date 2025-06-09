# frontend/roles/risker/pages/intraday_trigger_log_viewer.py

REQUIRES_CLIENT_CONTEXT = False

import os
import streamlit as st
from datetime import datetime, date, timedelta
from utils.config_loader import load_client_registry
from utils.time_utils import get_timestamps
from glob import glob
import json
import dateutil.parser
from core.request_context import RequestContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action
import pandas as pd
from io import BytesIO
from fpdf import FPDF

def load_latest_scan_log(client_id: str):
    log_dir = os.path.join("clients", client_id, "audit", "periodic_scan_logs")
    if not os.path.exists(log_dir):
        return None, None

    log_files = sorted(glob(os.path.join(log_dir, "*.jsonl")), reverse=True)
    for fpath in log_files:
        with open(fpath, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                try:
                    data = json.loads(lines[-1])
                    ts = data.get("timestamp")
                    return data, ts
                except Exception:
                    continue
    return None, None

def assess_risk_level(drawdown: float, silent_days: int) -> str:
    if drawdown <= -0.10 or silent_days >= 5:
        return "🔴 High"
    elif drawdown <= -0.05 or silent_days >= 2:
        return "🟠 Medium"
    return "🟢 Low"

def render(ctx: RequestContext):
    if not ctx.has_permission("risker.view_intraday_trigger_log"):
        st.warning("You do not have permission to view scan logs.")
        return

    record_user_action(ctx, module="intraday_trigger_log_viewer", action=UserAction.VIEW_INTRADAY_TRIGGER_LOGS)

    st.markdown("<h3 style='font-size: 1.7rem;'>📊 Intraday Trigger Logs</h3>", unsafe_allow_html=True)
    st.caption("View the latest intraday scan results per client, including risk triggers, drawdowns, and silent status.")

    date_filter = st.radio("Filter", ["Today", "This Week", "This Month", "All Time"], horizontal=True)
    risk_filter = st.selectbox("Risk Level Filter", ["All", "🔴 High", "🟠 Medium", "🟢 Low"], index=0)

    now = get_timestamps()["now_ny"]
    today_str = now.strftime("%Y-%m-%d")
    this_month_str = now.strftime("%Y-%m")
    this_week_start = (now - timedelta(days=now.weekday())).date()

    registry = load_client_registry()
    rows = []
    triggered_count = 0

    for client_id in sorted(registry.keys()):
        data, ts_raw = load_latest_scan_log(client_id)
        if ts_raw:
            try:
                ts_dt = dateutil.parser.parse(ts_raw)
                ts_fmt = ts_dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                ts_fmt = ts_raw
                ts_dt = None
        else:
            ts_fmt = "—"
            ts_dt = None

        if date_filter == "Today" and ts_dt and ts_dt.strftime("%Y-%m-%d") != today_str:
            continue
        if date_filter == "This Week" and ts_dt and ts_dt.date() < this_week_start:
            continue
        if date_filter == "This Month" and ts_dt and ts_dt.strftime("%Y-%m") != this_month_str:
            continue

        if data is None:
            risk_level = "—"
            silent_days = 0
            drawdown = 0.0
            row = {
                "Client": client_id,
                "Time": ts_fmt,
                "Net Value": "—",
                "Drawdown": "—",
                "Silent Mode": "—",
                "Triggered Assets": "—",
                "Risk Level": risk_level
            }
        else:
            drawdown = data.get("drawdown", 0.0)
            silent_days = data.get("silent_mode_days_left", 0)
            triggered_assets = data.get("triggered_assets", [])
            risk_level = assess_risk_level(drawdown, silent_days)
            if risk_level != "🟢 Low":
                triggered_count += 1
            row = {
                "Client": client_id,
                "Time": ts_fmt,
                "Net Value": f"{data.get('net_value', 0):,.2f}",
                "Drawdown": f"{drawdown:.2%}",
                "Silent Mode": silent_days,
                "Triggered Assets": ", ".join(triggered_assets) or "—",
                "Risk Level": risk_level
            }

        if risk_filter != "All" and risk_level != risk_filter:
            continue

        rows.append(row)

    total = len(rows)
    st.markdown(f"<div style='margin-bottom: 1rem; color: #aaa;'>Scanned Clients: <b>{total}</b> &nbsp;|&nbsp; Triggered: <b>{triggered_count}</b> &nbsp;|&nbsp; Date: <code>{now.strftime('%Y-%m-%d')}</code></div>", unsafe_allow_html=True)

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        if st.download_button("📥 Download CSV", data=csv_buffer.getvalue(), file_name="intraday_trigger_logs.csv", mime="text/csv"):
            record_user_action(ctx, module="intraday_trigger_view", action="download_csv", payload={"rows": len(df)})

        if st.button("📄 Export PDF Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Intraday Risk Summary Report", ln=True)
            pdf.cell(200, 10, txt=f"Period: {date_filter} | Date: {now.strftime('%Y-%m-%d')}", ln=True)
            pdf.cell(200, 10, txt=f"Triggered: {triggered_count} / {total}", ln=True)
            pdf.ln(8)
            for _, row in df.iterrows():
                line = f"{row['Client']} | {row['Time']} | Risk: {row['Risk Level']} | DD: {row['Drawdown']} | Silent: {row['Silent Mode']}"
                pdf.cell(200, 8, txt=line, ln=True)

            buffer = BytesIO()
            pdf.output(buffer)
            st.download_button("📥 Download PDF", data=buffer.getvalue(), file_name="trigger_report.pdf")
            record_user_action(ctx, module="intraday_trigger_view", action="download_pdf", payload={
                "rows": len(df),
                "triggered": triggered_count,
                "total": total
            })
    else:
        st.info("No scan logs found for the selected period.")