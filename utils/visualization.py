# utils/visualization.py

import os
import yaml
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.asset_utils import get_asset_category


def render_portfolio_pie(asset_data):
    """
    Draw a pie chart showing portfolio allocation.
    asset_data: list of dicts like [{"symbol": "AAPL", "value": 3000}, ...]
    """
    if not asset_data:
        st.info("No assets to display.")
        return

    fig = px.pie(
        asset_data,
        names="symbol",
        values="value",
        title="📊 Portfolio Allocation by Asset",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_candlestick_chart(symbol: str, df: pd.DataFrame):
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 1.5rem;
                padding-right: 1.5rem;
                max-width: 100% !important;
            }
            .element-container, .stPlotlyChart, .js-plotly-plot .plotly {
                width: 100% !important;
            }
        </style>
    """, unsafe_allow_html=True)

    try:
        if df.empty or "date" not in df.columns:
            st.warning("⚠️ No price data available.")
            return

        df = df.sort_values("date").dropna(subset=["open", "high", "low", "close", "volume"]).reset_index(drop=True)
        df["MA_5"] = df["close"].rolling(window=5).mean()
        df["MA_20"] = df["close"].rolling(window=20).mean()
        df["MA_60"] = df["close"].rolling(window=60).mean()

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df["date"], open=df["open"], high=df["high"],
            low=df["low"], close=df["close"],
            name="OHLC", increasing_line_color="#2ECC71", decreasing_line_color="#E74C3C",
            showlegend=False
        ))

        fig.add_trace(go.Scatter(x=df["date"], y=df["MA_5"], name="5-Day MA",
                                 line=dict(width=1.2, dash='dot'), marker_color="#FF5733"))
        fig.add_trace(go.Scatter(x=df["date"], y=df["MA_20"], name="20-Day MA",
                                 line=dict(width=1.2), marker_color="#3498DB"))
        fig.add_trace(go.Scatter(x=df["date"], y=df["MA_60"], name="60-Day MA",
                                 line=dict(width=1.2, dash='dash'), marker_color="#9B59B6"))

        fig.add_trace(go.Bar(x=df["date"], y=df["volume"], name="Volume",
                             yaxis="y2", marker_color="rgba(255, 255, 255, 0.15)", showlegend=False))

        fig.update_layout(
            height=750,
            margin=dict(l=20, r=20, t=50, b=30),
            title=dict(
                text=f"{symbol} — 100-Day Price Action & Moving Averages",
                x=0.01,
                xanchor='left',
                font=dict(size=20, family="Arial")
            ),
            xaxis=dict(title=None, showgrid=False, tickformat="%b %d", tickfont=dict(size=12)),
            yaxis=dict(title="Price", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12)),
            dragmode="pan"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to render candlestick chart for {symbol}: {str(e)}")


def render_intraday_chart(symbol: str, df: pd.DataFrame):
    if df.empty:
        st.warning("⚠️ No intraday data available.")
        return

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["close"],
        mode="lines+markers",
        name="Price",
        line=dict(color="#1f77b4", width=2.5, shape='spline'),
        marker=dict(size=3)
    ))

    fig.add_trace(go.Bar(
        x=df["timestamp"],
        y=df["volume"],
        yaxis="y2",
        name="Volume",
        marker_color="rgba(255, 255, 255, 0.15)",
        showlegend=False,
        opacity=0.6
    ))

    fig.update_layout(
        title=dict(
            text=f"{symbol} — Today's Intraday Price (5-min)",
            x=0.01,
            font=dict(size=20, family="Arial")
        ),
        xaxis=dict(title="Time", showgrid=False, tickangle=-30),
        yaxis=dict(title="Price", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, df["volume"].max() * 3]
        ),
        template="plotly_dark",
        height=450,
        margin=dict(l=20, r=20, t=50, b=30),
        hovermode="x unified",
        legend=dict(yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

from utils.format_utils import fmt_float, fmt_pct, fmt_money
import streamlit as st
import json
import io

def bool_display(val):
    return "✅ Yes" if val else "❌ No"

def render_trade_audit(record: dict):
    def safe(val, default="—"):
        return default if val in [None, "", {}, []] else val

    if "intent" not in record or "execution" not in record:
        st.error("❌ Incomplete audit record. Cannot render trade summary.")
        return

    intent = record.get("intent", {})
    approval = record.get("approval", {})
    signals = approval.get("signals", {})
    execution = record.get("execution", {})
    flags = record.get("risk_event_flags", {})
    context_info = record.get("execution_context", {})
    notes = intent.get("notes") or "—"
    status = execution.get("status", "N/A").upper()
    score = approval.get("score")

    executed = status == "EXECUTED"
    bg_color = "#1a472a" if executed else "#6a1b1b"
    text_color = "lime" if executed else "tomato"

    st.markdown(f"""
    <div style="padding: 1.2rem; background-color: {bg_color}; border-radius: 10px;">
    <h3 style="font-size: 1.6rem; margin-bottom: 0.3rem; color: white;">🛡️ Trade Outcome</h3>
    <b style="color: white;">Status:</b> <code style="color: {text_color};">{status}</code><br>
    <b style="color: white;">Decision:</b> <span style="color: white;">{approval.get("reason", "—")}</span><br>
    <b style="color: white;">Risk Score:</b> <span style="color: white;">{fmt_float(score)}</span>
    </div>
    """, unsafe_allow_html=True)

    if "intraday_snapshot" in record:
        render_intraday_snapshot(record["intraday_snapshot"])

    st.markdown("<h3 style='font-size: 1.6rem;'>🧾 Trade Lifecycle Journey</h3>", unsafe_allow_html=True)

    flow_content = f'''
**0b → Silent/KillSwitch Check**  
- Account Silent Mode: `{bool_display(record.get('cooling_off_triggered'))}`  
- KillSwitch Triggered: `{bool_display(flags.get('killswitch_triggered'))}`

⬇️

**1 → Intent + Risk Metadata**  
- ID: `{safe(intent.get('intent_id'))}`  
- Timestamp: `{safe(intent.get('timestamp'))}`  
- Symbol: `{safe(intent.get('symbol'))}`  
- Action: `{safe(intent.get('action'))}`  
- Quantity: `{safe(intent.get('quantity'))}`  
- Source: `{safe(intent.get('source'))}`  
- Source Type: `{safe(intent.get('source_type'))}`  
- Trader: `{safe(intent.get('trader_id'))}`  
- Strategy: `{safe(intent.get('strategy_id'))}`  
- Notes: `{safe(notes)}`

⬇️

**1b → Risk Assessment**  
- Score: `{fmt_float(score)}`  
- Risk Style: `{safe(approval.get('risk_style'))}`  
- Decision: `{safe(approval.get('reason'))}`  
- Reason Code: `{safe(approval.get('reason_code'))}`  
- Regime: `{safe(signals.get('regime'))}`  
- Volatility: `{fmt_pct(signals.get('volatility'))}`  
- VaR: `{fmt_pct(signals.get('var'))}`  
- CVaR: `{fmt_pct(signals.get('cvar'))}`

⬇️

**3 → Execution**  
- Executor Type: `{safe(record.get('executor_type'))}`  
- Broker: `{safe(context_info.get('broker'))}`  
- Dry Run: `{bool_display(context_info.get('dry_run'))}`  
- Expected Price: `{fmt_money(execution.get('expected_price'))}`  
- Actual Price: `{fmt_money(execution.get('price'))}`  
- Slippage: `{fmt_pct(execution.get('slippage_pct'))}`  
- Commission: `{fmt_money(execution.get('commission'))}`  
- Execution Latency: `{safe(execution.get('execution_latency_ms'), 'N/A')} ms`  
- Price Time: `{safe(execution.get('price_time'))}`  
- Status Code: `{safe(execution.get('status_code'))}`

⬇️

**4 → Logging**  
- Final Status: `{status}`  
- Timestamp: `{safe(intent.get('timestamp'))}`  
- System Version: `{safe(record.get('system_version'))}`  
- Client ID: `{safe(intent.get('client_id'))}`
'''
    st.markdown(f"<div style='border: 1px solid #333; border-radius: 12px; padding: 1.5rem; background-color: #111;'>{flow_content}</div>", unsafe_allow_html=True)

    # JSON download
    json_str = json.dumps(record, indent=2)
    json_bytes = io.BytesIO(json_str.encode("utf-8"))
    fname = f"audit_{safe(intent.get('intent_id'), 'trade')}.json"

    st.markdown("<h3 style='font-size: 1.6rem;'>📦 Export Audit Record</h3>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Full JSON",
        data=json_bytes,
        file_name=fname,
        mime="application/json"
    )




def render_intraday_snapshot(snapshot: dict):
    st.markdown("<h3 style='font-size: 1.6rem;'>🧩 Intraday Snapshot — Real-time Trigger Evaluation</h3>", unsafe_allow_html=True)
    st.markdown("Audit of all real-time risk conditions evaluated during this trade decision loop.")

    acc = snapshot.get("account", {})
    st.markdown("<h3 style='font-size: 1.4rem;'>🏦 Account Level</h3>", unsafe_allow_html=True)
    st.markdown(f"""
| Metric | Threshold | Observed | Triggered |
|--------|-----------|----------|-----------|
| Account Drawdown | < -5% | `{acc.get('drawdown', 0.0):.2%}` | {bool_display(acc.get('triggered'))} |
""")

    assets = snapshot.get("assets", {})
    if assets:
        st.markdown("<h3 style='font-size: 1.4rem;'>📊 Asset Level</h3>", unsafe_allow_html=True)
        for symbol, asset in assets.items():
            st.markdown(f"<h3 style='font-size: 1.2rem;'>📈 {symbol}</h3>", unsafe_allow_html=True)
            rows = []

            pd = asset.get("pos_drawdown")
            if pd is not None:
                rows.append(("Position Drawdown", "< -7%", f"{pd:.2%}", bool_display(asset["triggers"].get("drawdown"))))

            dd3 = asset.get("drawdown_3d")
            if dd3 is not None:
                rows.append(("3-day Drawdown", "< -10%", f"{dd3:.2%}", bool_display(asset["triggers"].get("drawdown_3d"))))

            slip = asset.get("slippage_pct")
            if slip is not None:
                rows.append(("Slippage", "> 0.5%", f"{slip:.2f}%", bool_display(asset["triggers"].get("slippage"))))

            ddays = asset.get("consec_down_days")
            rows.append(("Consecutive Down Days", "≥ 3", str(ddays), bool_display(asset["triggers"].get("consec_down"))))

            price = asset.get("current_price")
            prev = asset.get("prev_price")
            drop_pct = abs(price - prev) / prev if price and prev else None
            if drop_pct is not None:
                rows.append(("Intraday Drop", "> 8%", f"{drop_pct:.2%}", bool_display(asset["triggers"].get("intraday_drop"))))

            st.markdown(_build_table(rows), unsafe_allow_html=True)
    else:
        st.info("No asset-level silent checks recorded.")

def _build_table(rows):
    table = "<table style='width:100%; border-collapse: collapse;'>"
    table += "<tr><th style='text-align:left;'>Metric</th><th>Threshold</th><th>Observed</th><th>Triggered</th></tr>"
    for label, threshold, val, triggered in rows:
        table += f"<tr><td>{label}</td><td>{threshold}</td><td>{val}</td><td>{triggered}</td></tr>"
    table += "</table>"
    return table




import streamlit as st

# This component shows the approval + execution status of a single audit record.
# Typically used in: trade_form.py (Trader), audit_viewer.py (Auditor), etc.

def render_approval_status(record: dict):
    approval = record.get("approval", {})
    execution = record.get("execution", {})
    status = approval.get("status", "N/A").upper()
    exec_status = execution.get("status", "N/A").upper()
    reason = approval.get("reason", "—")

    color_map = {
        "APPROVED": "#00e676",
        "REJECTED": "#ff1744",
        "PENDING": "#ffab00",
        "N/A": "#9e9e9e",
        "BLOCKED": "#ff9100",
        "EXECUTED": "#2979ff",
        "SKIPPED": "#bdbdbd"
    }

    color = color_map.get(status, "#ccc")

    st.markdown(f"""
        <div style='padding: 0.6rem 1rem; border-left: 5px solid {color}; background-color: rgba(255,255,255,0.03); margin-bottom: 1.5rem;'>
            <div style='font-size: 1rem; font-weight: 600;'>🛡️ Approval Status: <span style='color: {color};'>{status}</span></div>
            <div style='font-size: 0.9rem; color: #bbb;'>Execution: <code>{exec_status}</code></div>
            <div style='font-size: 0.9rem; color: #bbb;'>Reason: {reason}</div>
        </div>
    """, unsafe_allow_html=True)

