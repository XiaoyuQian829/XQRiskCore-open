# frontend/roles/admin/pages/asset_manager.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
import yaml
import os
from core.request_context import RequestContext
from core.client_context import ClientContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view
from utils.config_loader import ConfigLoader

CONFIG_PATH = "config/symbol_category.yaml"


def render(ctx: RequestContext, client: ClientContext):
    if not ctx.has_permission("admin.edit_asset_config"):
        st.error("Access denied: insufficient permissions.")
        return

    record_user_view(ctx, module="asset_manager", action=UserAction.VIEW_ASSET_MANAGER)

    st.markdown("""
        <h3 style='margin-bottom: 1rem; font-size: 1.7rem;'>📁 Asset Category Config</h3>
        <div style='font-size: 0.9rem; color: #aaa;'>
        Manage global symbol pool via <code>symbol_category.yaml</code>. This defines the full set of available tradable symbols.
        Every client will select a subset of these symbols during profile creation.
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(CONFIG_PATH):
        st.error(f"Configuration file not found: {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r") as f:
        config_text = f.read()

    st.markdown("""
        <div style='font-size: 0.9rem; margin-bottom: 1rem;'>
        Edit the <code>symbol_category.yaml</code> file below. Group symbols like <code>AAPL</code>, <code>QQQ</code>, <code>BTC</code> under categories such as <strong>stocks</strong>, <strong>etfs</strong>, <strong>crypto</strong>.
        This global list will feed into each client's asset selection UI as the default universe.
        </div>
    """, unsafe_allow_html=True)

    updated_text = st.text_area(
        label="YAML Configuration",
        value=config_text,
        height=400,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save Changes"):
            try:
                parsed = yaml.safe_load(updated_text)
                with open(CONFIG_PATH, "w") as f:
                    f.write(updated_text)

                record_user_action(ctx, module="asset_manager", action="save_symbol_category", payload={"success": True})
                st.success("Configuration saved successfully.")
            except yaml.YAMLError as e:
                record_user_action(ctx, module="asset_manager", action="save_symbol_category", payload={"success": False, "error": str(e)})
                st.error(f"YAML Parsing Error: {e}")

    with col2:
        with st.expander("🔍 Preview Parsed Output"):
            try:
                parsed = yaml.safe_load(updated_text)
                st.json(parsed)
            except Exception:
                st.warning("Preview unavailable due to YAML parsing error.")

    # === 客户资产子集管理器 ===
    st.markdown(f"""
        <h3 style='margin-top: 2rem; font-size: 1.6rem;'>👤 Client Asset Subset</h3>
        <div style='font-size: 0.9rem; color: #aaa;'>
        Select a custom subset of symbols from the global pool for <code>{client.client_id}</code>. This subset will be saved to their <code>asset_config.yaml</code>.
        </div>
    """, unsafe_allow_html=True)

    loader = client.config_loader
    full_universe = loader.symbol_universe
    current_subset = loader.asset_config.get("symbol_universe", [])
    category_map = loader.symbol_category_map

    grouped = {}
    for symbol in full_universe:
        category = category_map.get(symbol, "Other")
        grouped.setdefault(category, []).append(symbol)

    # 每个 client 独立保存当前选中状态
    session_key = f"client_asset_selection_{client.client_id}"
    if session_key not in st.session_state:
        st.session_state[session_key] = set(current_subset)

    selected_set = st.session_state[session_key]

    col_all, col_none = st.columns(2)
    if col_all.button("✅ Select All"):
        st.session_state[session_key] = set(full_universe)
        selected_set = st.session_state[session_key]
    if col_none.button("❌ Clear All"):
        st.session_state[session_key] = set()
        selected_set = st.session_state[session_key]

    for category, symbols in grouped.items():
        with st.expander(f"📂 {category.title()} ({len(symbols)})", expanded=False):
            selected = st.multiselect(
                f"{category.title()} Symbols",
                options=symbols,
                default=[s for s in symbols if s in selected_set],
                key=f"multi_{category}_{client.client_id}"
            )
            selected_set.difference_update(symbols)
            selected_set.update(selected)

    st.caption(f"✅ Selected {len(selected_set)} symbols")
    with st.expander("📋 View Selected Symbols", expanded=False):
        st.code("\n".join(sorted(selected_set)), language="text")

    if st.button("💾 Save Client Asset Subset"):
        sorted_subset = sorted(selected_set)
        loader.asset_config["symbol_universe"] = sorted_subset
        loader.save_asset_config()
        record_user_action(ctx, module="asset_manager", action="update_client_asset_subset", payload={
            "client_id": client.client_id,
            "subset_size": len(sorted_subset)
        })
        st.success(f"✅ Saved {len(sorted_subset)} symbols to {client.client_id}'s asset_config.yaml")