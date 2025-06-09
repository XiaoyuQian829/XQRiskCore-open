# frontend/components/trade_form.py

REQUIRES_CLIENT_CONTEXT = True

import json
import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.trade_intent import TradeIntent
from services.trade_flow import run_trade_flow
from utils.visualization import render_candlestick_chart, render_intraday_chart, render_trade_audit

from core.request_context import RequestContext
from core.client_context import ClientContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

def render(ctx: RequestContext, client: ClientContext):
    st.markdown(f"""
    <div style='padding: 0.6rem 1rem; background-color: rgba(255,255,255,0.05); border-left: 4px solid #4dabf7; margin-bottom: 1rem; font-size: 0.95rem; color: #eee;'>
        📌 <strong style="color: #ccc;">Active Client:</strong> <code style="background-color: rgba(255,255,255,0.08); color: #00e676;">{client.client_id}</code>
    </div>
    """, unsafe_allow_html=True)

    if not ctx.has_permission("trader.submit_manual_trade"):
        st.warning("🚫 You do not have permission to submit manual trades.")
        return

    record_user_view(ctx, module="trade_form", action=UserAction.VIEW_TRADE_FORM)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.5rem;'>Manual Trade Interface</h3>
        <div style='font-size: 0.9rem; margin-bottom: 0.5rem; color: #aaa;'>Submit a manual buy/sell trade after inspecting the asset's chart.</div>
    """, unsafe_allow_html=True)

    trader_id = ctx.user_id or st.session_state.get("username", "unknown_trader")
    st.caption(f"👤 Logged in as: `{trader_id}`")
    st.caption(f"💼 Active Client: `{client.client_id}`")

    allowed_symbols = sorted(client.get_allowed_assets())
    if not allowed_symbols:
        st.error("No tradable symbols found in client's allowed asset subset.")
        return

    # Group allowed symbols by category
    category_map = client.config_loader.symbol_category_map
    symbol_groups = {}
    for symbol in allowed_symbols:
        category = category_map.get(symbol, "Other")
        symbol_groups.setdefault(category, []).append(symbol)

    # Dropdown for category and asset selection
    selected_category = st.selectbox("Asset Category", sorted(symbol_groups.keys()))
    selected_symbol = st.selectbox("Asset Symbol", sorted(symbol_groups[selected_category]))

    if not selected_symbol:
        return

    st.markdown("""
        <h4 style='margin-top: 1rem;'>Asset Price Charts</h4>
        <div style='font-size: 0.9rem; color: #bbb;'>Use the buttons below to view price history and intraday trends.</div>
    """, unsafe_allow_html=True)

    if "show_daily_chart" not in st.session_state:
        st.session_state["show_daily_chart"] = False
    if "show_intraday_chart" not in st.session_state:
        st.session_state["show_intraday_chart"] = False

    time_range = st.selectbox("🗓️ Select Time Range", options=["100d", "1mo", "1wk"], index=0, format_func=lambda x: {
        "100d": "Last 100 Days",
        "1mo": "This Month (~22 Days)",
        "1wk": "This Week (~5 Days)"
    }[x])

    cols = st.columns(2)
    if cols[0].button("📈 Show Price Chart"):
        st.session_state["show_daily_chart"] = True
        st.session_state["selected_time_range"] = time_range
    if cols[1].button("📊 Show Today's Intraday Chart"):
        st.session_state["show_intraday_chart"] = True

    if st.session_state["show_daily_chart"]:
        selected_range = st.session_state.get("selected_time_range", "100d")
        df_daily_full = client.market.get_price_history_100d(selected_symbol)
        days = {"100d": 100, "1mo": 22, "1wk": 5}[selected_range]
        df_trimmed = df_daily_full.tail(days)

        render_candlestick_chart(selected_symbol, df_trimmed)

        record_user_view(ctx, module="trade_form", action="view_chart_daily", payload={
            "symbol": selected_symbol,
            "time_range": selected_range
        })

    if st.session_state["show_intraday_chart"]:
        df_intraday = client.market.get_intraday(selected_symbol)
        render_intraday_chart(selected_symbol, df_intraday)
        record_user_view(ctx, module="trade_form", action="view_chart_intraday", payload={"symbol": selected_symbol})

    st.markdown("""
        <hr style='margin-top: 2rem; margin-bottom: 1rem;'>
        <h4 style='margin-bottom: 0.5rem;'>Submit Trade Order</h4>
        <div style='font-size: 0.9rem; color: #bbb;'>Select your trade action and quantity. The order will be submitted to the approval engine.</div>
    """, unsafe_allow_html=True)

    with st.form("manual_trade_form"):
        action = st.radio("Action", ["buy", "sell"], horizontal=True)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        submitted = st.form_submit_button("🚀 Submit Trade")

    if not submitted:
        return

    st.session_state.pop("last_trade_result", None)

    symbol = selected_symbol.upper()
    intent = TradeIntent(
        symbol=symbol,
        action=action,
        quantity=quantity,
        trader_id=trader_id,
        client_id=client.client_id,
        source_type="manual",
        source="manual",
        strategy_id=None,
        notes=""
    )

    record_user_action(
        ctx,
        module="trade_form",
        action=UserAction.SUBMIT_FORM,
        payload={"symbol": symbol, "action": action, "quantity": quantity}
    )

    result = run_trade_flow(client, intent)

    render_trade_audit(result.audit_record)

"""    
    if result.status == "executed" and getattr(result, "audit_record", None):
        render_trade_audit(result.audit_record)
    else:
        st.warning("Trade executed, but audit record not available.")
"""
