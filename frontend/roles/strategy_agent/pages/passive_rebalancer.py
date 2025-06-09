# frontend/roles/strategy_agent/pages/passive_rebalancer.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
from scheduler.rebalance_scheduler import run_scheduled_rebalance
from core.request_context import RequestContext
from core.client_context import ClientContext
from audit.action_logger import record_user_action, record_user_view
from utils.user_action import UserAction
import traceback

def render(ctx: RequestContext, client: ClientContext):
    if not ctx.has_permission("strategy_agent.run_passive_rebalance"):
        st.warning("🚫 You do not have permission to run passive rebalance.")
        return

    record_user_view(ctx, module="passive_rebalancer", action=UserAction.VIEW_PASSIVE_REBALANCER)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>🧘 Passive Rebalancer</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            Trigger a full passive rebalance for your portfolio based on regime state and multi-factor risk score.<br>
            The system will scan asset schedules and generate TradeIntents for assets scheduled for today.
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Run Passive Rebalance Now", use_container_width=True):
        record_user_action(ctx, module="passive_rebalancer", action=UserAction.SUBMIT_FORM, payload={
            "client_id": client.client_id
        })

        try:
            run_scheduled_rebalance(client.client_id)

            record_user_action(ctx, module="passive_rebalancer", action=UserAction.ACTION_SUCCESS)
            st.toast("✅ Passive rebalance completed successfully.")
            st.success("Rebalance finished. TradeIntents have been generated and executed (if applicable).")

        except Exception as e:
            error_msg = str(e)
            # Optional: capture traceback for debugging
            traceback_str = traceback.format_exc()
            record_user_action(ctx, module="passive_rebalancer", action=UserAction.ACTION_ERROR, payload={
                "error": error_msg,
                "traceback": traceback_str
            })
            st.error(f"❌ An error occurred during passive rebalance:\n\n{error_msg}")
