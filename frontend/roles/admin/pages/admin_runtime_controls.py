# frontend/roles/admin/pages/runtime_controls.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
import pandas as pd

from core.request_context import RequestContext
from core.client_context import ClientContext
from risk_engine.triggers.killswitch import KillSwitchManager
from utils.time_utils import get_timestamps
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

def render(ctx: RequestContext, client: ClientContext):
#    if not ctx.has_permission("admin.trigger_global_killswitch"):
#        st.error("❌ You do not have permission to access runtime controls.")
#        return

    # ✅ 记录查看行为
    record_user_view(ctx, module="runtime_controls", action=UserAction.VIEW_RUNTIME_CONTROLS)

    # ✅ 页面主体
    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>⚙️ Runtime Risk Control Panel</h3>
        <div style='font-size: 0.9rem; color: #bbb; margin-bottom: 1rem;'>
            Manage silent mode and kill-switch protections for account and asset level controls.
        </div>
    """, unsafe_allow_html=True)

    state = client.portfolio_state
    ks = KillSwitchManager(client)
    admin_user = ctx.user_id or "admin"

    with st.expander("🧾 Debug Info", expanded=False):
        st.markdown(f"**User ID:** `{ctx.user_id}`")
        st.markdown(f"**Role:** `{ctx.role}`")
        st.markdown(f"**Client ID:** `{client.client_id}`")
        st.markdown(f"**Source:** `{ctx.source}`")
        st.markdown("**Permissions:**")
        st.json(ctx.permissions)

    # === Account-Level Controls ===
    st.subheader("🔒 Account-Level Controls")

    col1, _ = st.columns(2)
    with col1:
        silent_active = state.get("silent_mode_days_left", 0) > 0
        if not silent_active:
            if st.button("Trigger Account Silent (5 days)"):
                ks.trigger_silent_all(days=5, reason="Manual trigger from admin", user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="trigger_account_silent", payload={"client_id": client.client_id})
                st.success("Account silent mode triggered.")
                st.rerun()
        else:
            if st.button("Release Account Silent"):
                ks.release_silent_all(user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="release_account_silent", payload={"client_id": client.client_id})
                st.success("Account silent mode released.")
                st.rerun()

    col2, _ = st.columns(2)
    with col2:
        killswitch_active = state.get("killswitch_active", False)
        if not killswitch_active:
            if st.button("Trigger Account Kill Switch"):
                ks.trigger_killswitch_all(reason="Manual kill", user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="trigger_account_killswitch", payload={"client_id": client.client_id})
                st.success("Account kill-switch activated.")
                st.rerun()
        else:
            if st.button("Release Account Kill Switch"):
                ks.release_killswitch_all(user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="release_account_killswitch", payload={"client_id": client.client_id})
                st.success("Account kill-switch released.")
                st.rerun()

    st.markdown("<h4 style='margin-top: 2rem;'>📋 Account Risk Status</h4>", unsafe_allow_html=True)
    account_info = {
        "Silent Mode": "ON" if state.get("silent_mode", False) else "OFF",
        "Silent Days Left": state.get("silent_mode_days_left", 0),
        "Silent Reason": state.get("silent_reason", "-"),
        "KillSwitch Active": "ON" if state.get("killswitch_active", False) else "OFF",
        "KillSwitch Reason": state.get("killswitch_reason", "-"),
        "Last Updated": state.get("last_updated", get_timestamps()["ny_time_str"])
    }
    st.table(account_info)

    st.markdown("---")
    st.subheader("📦 Asset-Level Controls")

    asset_list = list(client.portfolio.assets.keys())
    if not asset_list:
        st.info("No assets in portfolio.")
        return

    selected_asset = st.selectbox("Select Asset", asset_list)
    asset = client.portfolio.assets[selected_asset]
    silent_days = st.slider("Silent Days", 1, 10, 2)

    col3, _ = st.columns(2)
    with col3:
        silent_active = asset.get("silent_days_left", 0) > 0
        if not silent_active:
            if st.button("Trigger Silent for Asset"):
                ks.trigger_silent(selected_asset, days=silent_days, reason="Manual silent", user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="trigger_asset_silent", payload={"symbol": selected_asset})
                st.success(f"{selected_asset} entered silent mode for {silent_days} days.")
                st.rerun()
        else:
            if st.button("Release Silent for Asset"):
                ks.release_silent(selected_asset, user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="release_asset_silent", payload={"symbol": selected_asset})
                st.success(f"{selected_asset} silent mode released.")
                st.rerun()

    col4, _ = st.columns(2)
    with col4:
        killswitch_active = asset.get("killswitch", False)
        if not killswitch_active:
            if st.button("Trigger Kill Switch for Asset"):
                ks.trigger_killswitch(selected_asset, reason="Manual kill", user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="trigger_asset_killswitch", payload={"symbol": selected_asset})
                st.success(f"{selected_asset} kill-switched.")
                st.rerun()
        else:
            if st.button("Release Kill Switch for Asset"):
                ks.release_killswitch(selected_asset, user_id=admin_user)
                client.save()
                record_user_action(ctx, module="runtime_controls", action="release_asset_killswitch", payload={"symbol": selected_asset})
                st.success(f"{selected_asset} kill-switch released.")
                st.rerun()

    st.markdown("---")
    st.subheader("🧾 Asset Risk Summary")

    asset_status = []
    for symbol, asset in state.get("assets", {}).items():
        silent = asset.get("silent_days_left", 0)
        ks_active = asset.get("killswitch", False)
        color_bar = "🟩"
        if ks_active:
            color_bar = "🟥"
        elif silent > 0:
            color_bar = "🟨"

        asset_status.append({
            "Status": color_bar,
            "Symbol": str(symbol),
            "Position": str(asset.get("position", 0)),
            "Silent Days Left": str(silent),
            "Killswitch": "✅" if ks_active else "❌",
            "Silent Reason": str(asset.get("silent_trigger_reason", "")),
            "Holding Days": str(asset.get("holding_days", 0)),
            "Drawdown %": str(round(asset.get("drawdown_pct", 0.0) * 100, 3))
        })

    df = pd.DataFrame(asset_status).astype(str)
    st.dataframe(df, use_container_width=True)


