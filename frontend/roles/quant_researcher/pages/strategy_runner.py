# frontend/roles/strategy_agent/pages/strategy_runner.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
import time
from datetime import datetime
import pandas as pd

from core.request_context import RequestContext
from core.client_context import ClientContext
from strategy.strategy_runner_entry import run_strategies_for_client
from strategy.strategy_manager import StrategyManager
from strategy.mean_reversion_bot import MeanReversionBot
from strategy.momentum_bot import MomentumStrategy
from services.trade_flow import run_trade_flow
from audit.action_logger import record_user_action, record_user_view
from core.trade_intent import TradeIntent
from utils.user_action import UserAction

STRATEGY_REGISTRY = {
    "Mean Reversion": MeanReversionBot,
    "Momentum": MomentumStrategy
}

def render(ctx: RequestContext, client: ClientContext):

    if not ctx.has_permission("quant_researcher.run_strategy"):
        st.warning("\U0001F6AB You do not have permission to run strategy.")
        return

    # === 初始化 session_state ===
    if "strategy_agent_state" not in st.session_state:
        st.session_state.strategy_agent_state = {}

    state = st.session_state.strategy_agent_state
    state.setdefault("running", False)
    state.setdefault("log", [])
    state.setdefault("status", {})
    state.setdefault("last_run_time", None)
    state.setdefault("results", None)

    record_user_view(ctx, module="strategy_runner", action=UserAction.VIEW_STRATEGY_RUNNER)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>🚀 Strategy Runner</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            Select strategy modules and apply them to selected symbols. All generated intents will be processed through the risk-controlled execution flow.
        </div>
    """, unsafe_allow_html=True)

    # === 筛选策略和资产 ===
    allowed_symbols = sorted(client.get_allowed_assets())
    category_map = client.config_loader.symbol_category_map
    symbol_groups = {}
    for symbol in allowed_symbols:
        category = category_map.get(symbol, "Other")
        symbol_groups.setdefault(category, []).append(symbol)

    selected_category = st.selectbox("📁 Asset Category", sorted(symbol_groups))
    selected_symbols = st.multiselect("🎯 Select Symbols", sorted(symbol_groups[selected_category]), default=symbol_groups[selected_category])
    selected_strategies = st.multiselect("🧠 Select Strategies", list(STRATEGY_REGISTRY), default=list(STRATEGY_REGISTRY))

    run_mode = st.radio("Execution Mode", ["Manual", "Timed Loop"], horizontal=True)
    interval_sec = st.number_input("Loop Interval (sec)", value=10, min_value=1) if run_mode == "Timed Loop" else None

    # === 控制按钮 ===
    col1, col2 = st.columns(2)
    if col1.button("🚀 Start Execution", use_container_width=True):
        state["running"] = True
        state["log"] = []
        state["status"] = {}
        st.toast("✅ Execution started.")
        record_user_action(ctx, module="strategy_runner", action="start_execution", payload={
            "strategies": selected_strategies,
            "symbols": selected_symbols,
            "mode": run_mode
        })

    if col2.button("⛔ Stop Execution", use_container_width=True):
        state["running"] = False
        st.toast("🛑 Execution stopped.")
        record_user_action(ctx, module="strategy_runner", action="stop_execution")

    # === 执行逻辑 ===
    if state["running"]:
        sm = StrategyManager(client.client_id)
        for name in selected_strategies:
            sm.register(name, STRATEGY_REGISTRY[name])

        def run_once():
            results = []
            for name in selected_strategies:
                strategy = sm.instances.get(name)
                for symbol in selected_symbols:
                    try:
                        intents = strategy.generate_trade_intents(symbol)
                        for intent in intents:
                            intent.source_type = "strategy"
                            intent.source = name
                            intent.client_id = client.client_id
                            result = run_trade_flow(client, intent)
                            results.append(result)
                            state["status"][(name, symbol)] = result.result.get("status", "N/A")
                    except Exception as e:
                        state["status"][(name, symbol)] = f"❌ Error: {e}"
            return results

        if run_mode == "Manual":
            with st.spinner("Running once..."):
                results = run_once()
                state["log"].extend([(datetime.now(), r) for r in results])
                st.success(f"✅ Ran once: {len(results)} trade intents executed.")

        elif run_mode == "Timed Loop":
            with st.spinner("Running loop... press Stop to interrupt."):
                while state["running"]:
                    results = run_once()
                    state["log"].extend([(datetime.now(), r) for r in results])
                    time.sleep(interval_sec)
                    st.rerun()

    # === 执行状态展示 ===
    st.markdown("---")
    st.markdown("### 📈 Strategy-Symbol Execution Status")
    status_map = state.get("status", {})
    if not status_map:
        st.info("No execution status yet.")
    else:
        df = pd.DataFrame([
            {"Strategy": k[0], "Symbol": k[1], "Last Status": v}
            for k, v in status_map.items()
        ])
        st.dataframe(df, use_container_width=True)

    # === 执行日志展示 ===
    st.markdown("---")
    st.markdown("### 📜 Strategy Execution Log")
    logs = state["log"]
    if not logs:
        st.info("No strategy execution log yet.")
    else:
        for ts, r in reversed(logs[-10:]):
            intent = r.intent
            symbol = intent.symbol
            action = intent.action.upper()
            status = r.result.get("status", "N/A")
            reason = r.result.get("reason", "—")
            approved = status == "executed"

            badge = "✅" if approved else "❌"
            st.markdown(f"""
                <div style='border-left: 4px solid #888; padding: 0.5rem; margin-bottom: 0.6rem; background-color: rgba(255,255,255,0.05);'>
                    <strong>{badge} {ts.strftime('%H:%M:%S')} | {symbol} | {action} → {status}</strong><br>
                    <span style='color: #bbb;'>{reason}</span>
                </div>
            """, unsafe_allow_html=True)
