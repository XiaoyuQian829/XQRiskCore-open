# dev_tools/strategy_batch_runner.py

# ⚠️ DEPRECATED
# This script has been replaced by the Streamlit UI version under
# frontend/roles/strategy_agent/pages/strategy_runner.py
# Retained for legacy CLI testing or batch development.

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strategy.strategy_manager import StrategyManager
from strategy.momentum_bot import MomentumBot
from strategy.mean_reversion_bot import MeanReversionBot
from services.trade_flow import run_trade_flow

def run_all_strategies_for(client_id: str, symbols: list):
    print(f"🧠 Running all registered strategies for {client_id}...")

    manager = StrategyManager(client_id)
    manager.register("momentum", MomentumBot)
    manager.register("mean_reversion", MeanReversionBot)

    intents = manager.run_all(symbols)
    print(f"📝 {len(intents)} intents generated.")

    ctx = manager.get_client_context()
    for intent in intents:
        print(f"\n=== {intent.symbol} ({intent.source}) ===")
        result = run_trade_flow(ctx, intent)
        print(f"🧾 Result: {result.status.upper()} | Reason: {result.reason}")
        if result.status == "executed":
            print(f"✅ Trade executed at ${result.price:.2f}")

if __name__ == "__main__":
    run_all_strategies_for(client_id="Allan", symbols=["AAPL", "SPY", "TLT", "JPM"])
