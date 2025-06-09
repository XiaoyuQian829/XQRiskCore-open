# frontend/roles/auditor/pages/components/intent_tracer.py

REQUIRES_CLIENT_CONTEXT = True

import os, json
import streamlit as st
import pandas as pd
from glob import glob
from datetime import datetime
import pytz

from utils.config_loader import load_client_registry
from core.request_context import RequestContext
from core.client_context import ClientContext
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

def search_intent_in_audit(client_id, intent_id=None):
    base = f"clients/{client_id}/audit"
    results = []
    for module in os.listdir(base):
        module_path = os.path.join(base, module)
        if not os.path.isdir(module_path):
            continue
        for file in glob(f"{module_path}/*.json*"):
            with open(file, "r") as f:
                lines = f.readlines() if file.endswith(".jsonl") else [f.read()]
                for line in lines:
                    try:
                        record = json.loads(line)
                        found_id = record.get("intent", {}).get("intent_id")
                        if intent_id is None or found_id == intent_id:
                            results.append((file, record))
                    except:
                        continue
    return results

def format_time(timestamp):
    try:
        dt = datetime.fromisoformat(timestamp)
        ny_tz = pytz.timezone("America/New_York")
        dt = dt.astimezone(ny_tz)
        return dt.strftime("%Y-%m-%d %H:%M:%S") + " ET"
    except:
        return timestamp

def render(ctx: RequestContext, client: ClientContext):
    if not ctx.has_permission("auditor.trace_intent"):
        st.warning("❌ You do not have permission to trace trade intents.")
        return

    record_user_view(ctx, module="intent_tracer", action=UserAction.VIEW_INTENT_TRACER)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>🔍 Intent Tracer</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            Trace recent or specific trade intents by intent ID. See approval, execution, feedback and kill-switch flags across modules.
        </div>
    """, unsafe_allow_html=True)

    st.caption(f"📌 Active Client: `{client.client_id}`")

    # === Recent Intents ===
    st.markdown("### 📜 Recent Intents")
    recent_matches = search_intent_in_audit(client.client_id)
    summarized = []

    for path, record in recent_matches:
        intent = record.get("intent", {})
        approval = record.get("approval", {})
        execution = record.get("execution", {})
        if not intent.get("intent_id"):
            continue

        source = intent.get("source", "-")
        source_type = intent.get("source_type", "-")
        strategy_id = intent.get("strategy_id")
        trader_id = intent.get("trader_id")

        if source_type == "manual":
            source_type_label = "Manual"
            source_id = trader_id or "?"
        elif source == "passive":
            source_type_label = "Passive"
            source_id = "passive_engine"
        elif strategy_id:
            source_type_label = "Strategy"
            source_id = strategy_id
        else:
            source_type_label = "System"
            source_id = source

        summarized.append({
            "Client": intent.get("client_id", "-"),
            "Intent ID": intent.get("intent_id"),
            "Symbol": intent.get("symbol", "-"),
            "Action": intent.get("action", "-"),
            "Source Type": source_type_label,
            "Source ID": source_id,
            "Approved": "✅" if approval.get("approved") else "❌",
            "Score": approval.get("score", "-"),
            "Slip": execution.get("slippage_pct", 0.0),
            "Commission": execution.get("commission", 0.0),
            "Time": format_time(intent.get("timestamp", "-"))
        })

    if summarized:
        df = pd.DataFrame(summarized).sort_values("Time", ascending=False).reset_index(drop=True)

        source_filter = st.selectbox("Filter by Source Type", options=["All"] + sorted(df["Source Type"].unique()))
        if source_filter != "All":
            df = df[df["Source Type"] == source_filter].reset_index(drop=True)

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No recent intent records found.")

    # === Intent ID Search ===
    st.markdown("---")
    st.markdown("### 🔎 Search by Intent ID")

    intent_id = st.text_input("Enter Intent ID")
    if st.button("Trace Intent") and intent_id:
        record_user_action(ctx, module="intent_tracer", action=UserAction.SUBMIT_FORM, payload={"intent_id": intent_id})

        matches = search_intent_in_audit(client.client_id, intent_id)
        if not matches:
            st.warning("No matching intent record found.")
        else:
            st.success(f"Found {len(matches)} matching record(s).")

            for path, record in matches:
                intent = record.get("intent", {})
                approval = record.get("approval", {})
                execution = record.get("execution", {})
                snapshot = record.get("portfolio_snapshot", {})
                silent = record.get("silent", {})
                killswitch = record.get("killswitch", {})
                feedback = record.get("feedback")

                symbol = intent.get("symbol", "?")
                action = intent.get("action", "?")
                price = execution.get("price", "?")
                approved = approval.get("approved", False)
                slip = execution.get("slippage_pct", 0.0)
                latency = execution.get("execution_latency_ms", 0)
                commission = execution.get("commission", 0.0)

                label = f"{symbol} | {action.upper()} @ {price} | Approved: {'✅' if approved else '❌'} | Slip: {slip:.3%} | Commission: ${commission:.4f} | Latency: {latency}ms"
                with st.expander(label):
                    record_user_view(ctx, module="intent_tracer", action="view_trace_result", payload={"intent_id": intent.get("intent_id")})

                    st.markdown(f"**🗂 File**: `{os.path.basename(path)}`")

                    st.markdown("#### 🧠 Trade Intent")
                    st.json(intent)

                    st.markdown("#### 🛡️ Risk Approval")
                    st.json(approval or {"info": "No approval record found."})

                    st.markdown("#### ✅ Execution Record")
                    if execution:
                        st.json(execution)
                        st.markdown(f"**Commission Paid:** ${commission:.4f}")
                    else:
                        st.info("No execution occurred.")

                    st.markdown("#### 📊 Portfolio Snapshot")
                    st.json(snapshot or {"info": "No portfolio snapshot recorded."})

                    st.markdown("#### 🚫 KillSwitch / Silent Mode")
                    if silent or killswitch:
                        st.json({"silent": silent, "killswitch": killswitch})
                    else:
                        st.success("No blocking status recorded.")

                    st.markdown("#### 🔁 Post-Trade Feedback")
                    st.json(feedback or {"info": "No post-trade feedback available."})

