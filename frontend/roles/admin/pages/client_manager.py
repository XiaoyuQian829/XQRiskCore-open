# frontend/roles/admin/pages/client_manager.py

REQUIRES_CLIENT_CONTEXT = False

import streamlit as st
import pandas as pd
import yaml
import io
import os
from pathlib import Path

from admin.add_client import create_client_from_config
from core.request_context import RequestContext
from utils.config_loader import (
    load_client_registry,
    save_client_registry,
    load_all_symbols_from_category,
    load_client_asset_config,
    save_client_asset_config
)
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

DEFAULT_DRY_RUN_ENFORCED = True
FORCED_BROKER = "alpaca"

def render_info_notice(msg: str):
    st.markdown(f"<div style='font-size: 0.9rem; color: #bbb;'>{msg}</div>", unsafe_allow_html=True)

def render_small_header(text: str, level: int = 4):
    size = {3: "1.5rem", 4: "1.3rem", 5: "1.1rem"}.get(level, "1.3rem")
    st.markdown(f"<h{level} style='font-size: {size}; margin-top: 1rem;'>{text}</h{level}>", unsafe_allow_html=True)

def render_broker_notice(key_prefix: str):
    st.selectbox("Broker (locked)", [FORCED_BROKER], index=0, disabled=True, key=f"{key_prefix}_broker_locked")
    render_info_notice("\U0001f512 Broker is currently locked to <code>Alpaca</code> for development purposes.<br>Future releases will support other brokers (e.g., IBKR, Tiger, FIX).")

def render(ctx: RequestContext):
    if not ctx.has_permission("admin.create_client"):
        st.error("Access denied: insufficient permissions.")
        return

    record_user_view(ctx, module="client_manager", action=UserAction.VIEW_CLIENT_MANAGER)

    render_small_header("🏢 Client Profile Management", level=4)
    st.markdown("""
        <div style='font-size: 0.9rem; color: #bbb;'>
            Overview of all registered clients. Displays client configuration from <code>client_registry.yaml</code> and risk constraints from <code>asset_config.yaml</code>.
        </div>
    """, unsafe_allow_html=True)

    registry = load_client_registry()

    data = []
    for cid, info in registry.items():
        asset_cfg = load_client_asset_config(cid)
        constraints = asset_cfg.get("risk_constraints", {})
        data.append({
            "Client ID": cid,
            "Name": info.get("name", "-"),
            "API Provider": info.get("api_provider", "-"),
            "Broker": info.get("broker", "-"),
            "Dry Run": "✅" if info.get("dry_run", False) else "❌",
            "Created At": info.get("created_at", "-"),
            "Risk Style": asset_cfg.get("risk_style", "-"),
            "Max DD (%)": constraints.get("max_drawdown_pct", "-"),
            "Min Hold (days)": constraints.get("min_holding_days", "-"),
            "Silent After Loss (days)": constraints.get("silent_after_loss_days", "-"),
            "#Assets Allowed": len(asset_cfg.get("symbol_universe", []))
        })

    df = pd.DataFrame(data)
    df.index = [str(i + 1) for i in range(len(df))]
    df.index.name = "#"
    st.dataframe(df, use_container_width=True)

    with st.expander("📄 Export Client Config"):
        export_client_id = st.selectbox("Select a client to export", list(registry.keys()), key="export_select")
        export_data = registry[export_client_id]
        yaml_str = yaml.dump(export_data, sort_keys=False)
        st.download_button(
            label="📁 Download YAML",
            data=io.BytesIO(yaml_str.encode("utf-8")),
            file_name=f"{export_client_id}_config.yaml",
            mime="text/yaml"
        )

    with st.expander("🛠️ Edit Client Configuration"):
        selected_client = st.selectbox("Select a client to edit", list(registry.keys()), key="edit_client_select")
        selected_entry = registry[selected_client]
        client_asset_config = load_client_asset_config(selected_client)
        current_constraints = client_asset_config.get("risk_constraints", {})

        with st.form(key="edit_client_form"):
            render_small_header(f"🔧 Editing '{selected_client}'", level=5)

            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=selected_entry.get("name", ""), key="edit_name")
                new_risk_style = st.selectbox("Risk Style", ["conservative", "moderate", "aggressive"],
                                              index=["conservative", "moderate", "aggressive"].index(
                                                  selected_entry.get("risk_style", "conservative")),
                                              key="edit_risk_style")
            with col2:
                new_api_provider = st.selectbox("API Provider", ["alpha_vantage", "polygon", "yahoo", "tiingo"],
                                                index=["alpha_vantage", "polygon", "yahoo", "tiingo"].index(
                                                    selected_entry.get("api_provider", "alpha_vantage")),
                                                key="edit_api_provider")
                new_api_key = st.text_input("API Key", value=selected_entry.get("api_key", ""), key="edit_api_key")

            symbol_list = client_asset_config.get("symbol_universe", [])
            st.markdown(f"**🧮 Assets Assigned:** {len(symbol_list)} symbols &nbsp;&nbsp; <span style='color: #bbb; font-size: 0.85rem;'>⚙️ Edit in Admin → Tradable Asset Config</span>", unsafe_allow_html=True)

            render_info_notice("📊 All data currently uses the developer's Alpha Vantage API key (for testing).")
            render_broker_notice("edit")
            st.checkbox("Dry Run", value=True, disabled=True, key="edit_dry_run_enforced")

            st.markdown("---")
            render_small_header("⚖️ Risk Constraints", level=5)

            col1, col2, col3 = st.columns(3)
            with col1:
                new_max_dd = st.slider("Max Drawdown (%)", 1, 50,
                                       value=current_constraints.get("max_drawdown_pct", 10),
                                       key="edit_cfg_max_dd")
            with col2:
                new_min_hold = st.slider("Min Holding Days", 1, 30,
                                         value=current_constraints.get("min_holding_days", 3),
                                         key="edit_cfg_min_days")
            with col3:
                new_silent = st.slider("Silent Days After Loss", 0, 30,
                                       value=current_constraints.get("silent_after_loss_days", 5),
                                       key="edit_cfg_silent")

            if st.form_submit_button("💾 Save All Settings"):
                selected_entry.update({
                    "name": new_name,
                    "risk_style": new_risk_style,
                    "api_provider": new_api_provider,
                    "api_key": new_api_key,
                    "broker": FORCED_BROKER,
                    "assets": selected_entry.get("assets", []),
                    "dry_run": DEFAULT_DRY_RUN_ENFORCED
                })
                save_client_registry(registry)

                client_asset_config["risk_style"] = new_risk_style
                client_asset_config["risk_constraints"] = {
                    "max_drawdown_pct": new_max_dd,
                    "min_holding_days": new_min_hold,
                    "silent_after_loss_days": new_silent
                }
                save_client_asset_config(selected_client, client_asset_config)

                record_user_action(ctx, module="client_manager", action="update_client_config", payload={
                    "client_id": selected_client,
                    "name": new_name,
                    "risk_style": new_risk_style,
                    "assets_count": len(symbol_list),
                    "api_provider": new_api_provider
                })

                st.success(f"Client '{selected_client}' updated.")
                st.rerun()

    with st.expander("➕ Create New Client Profile", expanded=True):
        client_id = st.text_input("Client ID *", key="create_client_id")
        client_name = st.text_input("Client Name *", key="create_client_name")
        api_provider = st.selectbox("Market Data Provider *", ["alpha_vantage", "polygon", "yahoo", "tiingo"], key="create_api_provider")
        api_key = st.text_input(f"{api_provider.upper()} API Key", key="create_api_key")
        base_capital = st.number_input("Base Capital *", min_value=1000, value=100000, key="create_base_capital")
        risk_style = st.selectbox("Risk Style *", ["conservative", "moderate", "aggressive"], key="create_risk_style")
        st.checkbox("Dry Run Mode", value=True, disabled=True, key="create_dry_run_enforced")

        render_broker_notice("create")
        alpaca_key = st.text_input("Alpaca API Key", key="alpaca_key")
        alpaca_secret = st.text_input("Alpaca Secret Key", type="password", key="alpaca_secret")
        broker_keys = {"key": alpaca_key, "secret": alpaca_secret}

        render_small_header("Default Risk Control Settings", level=5)
        max_drawdown = st.slider("Max Drawdown (%)", 1, 50, 10, key="max_drawdown")
        min_days = st.slider("Minimum Holding Days", 1, 30, 3, key="min_holding_days")
        silent_days = st.slider("Silent Mode After Loss (days)", 0, 30, 5, key="silent_days")

        render_small_header("Intraday Trigger Settings", level=5)
        enable_intraday_trigger = st.toggle("Enable Intraday Trigger", value=True, key="create_enable_intraday")
        intraday_trigger_interval = st.slider("Trigger Interval (minutes)", 5, 120, 10, step=5, key="create_interval_minutes")

        all_symbols = load_all_symbols_from_category()
        st.info(f"🚫 Asset list is fixed. {len(all_symbols)} symbols loaded from `symbol_category.yaml`. Assets cannot be changed here.")

        if st.button("✅ Create Client", key="create_client_button"):
            if not client_id.strip():
                st.warning("Client ID is required.")
                return
            if not client_name.strip():
                st.warning("Client Name is required.")
                return

            config = {
                "client_id": client_id.strip(),
                "name": client_name.strip(),
                "api_provider": api_provider,
                "api_key": api_key,
                "base_capital": base_capital,
                "assets": all_symbols,
                "risk_style": risk_style,
                "dry_run": DEFAULT_DRY_RUN_ENFORCED,
                "broker": FORCED_BROKER,
                "broker_keys": broker_keys,
                "enable_intraday_trigger": enable_intraday_trigger,
                "intraday_trigger_interval_minutes": intraday_trigger_interval,
                "max_drawdown_pct": max_drawdown,
                "min_holding_days": min_days,
                "silent_after_loss_days": silent_days
            }

            create_client_from_config(config)
            record_user_action(ctx, module="client_manager", action="create_client", payload={"client_id": client_id})
            st.success(f"Client '{client_id}' created successfully.")
            st.rerun()
