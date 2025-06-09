# services/rebalance_driver.py
"""
Weekly Risk-Aware Rebalance Driver
==================================

This script loads system-wide risk signal, computes target exposures,
and generates and executes passive adjustment TradeIntents via the
unified trade_flow pipeline.

• Input: portfolio state + risk signal
• Output: executed passive rebalancing trades
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.passive.rebalance_engine import PassiveRebalancer
from services.trade_flow import run_trade_flow
from core.client_context import ClientContext


def run_weekly_rebalance(client_id: str):
    print(f"\n🟢 [Rebalancer] Starting passive rebalance for client {client_id}...")
    
    # === Step 1: Load passive rebalancer ===
    rebalancer = PassiveRebalancer(client_id)
    intents = rebalancer.run()

    if not intents:
        print("✅ No rebalancing needed. All weights aligned.")
        return []

    # === Step 2: Execute each intent using unified trade flow ===
    ctx = ClientContext(client_id)
    results = []

    for intent in intents:
        print(f"⚙️  Executing rebalance intent: {intent.symbol} {intent.action} {intent.quantity}")
        result = run_trade_flow(ctx, intent)
        results.append(result)

    print(f"✅ Passive rebalancing completed. {len(results)} trades executed.")
    return results


# === Optional entry point ===
if __name__ == "__main__":
    run_weekly_rebalance("Allan")