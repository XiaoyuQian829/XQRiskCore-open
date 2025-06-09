# strategy/strategy_runner_entry.py

from strategy.strategy_manager import StrategyManager
from strategy.mean_reversion_bot import MeanReversionBot
from strategy.momentum_bot import MomentumStrategy
from services.trade_flow import run_trade_flow

def run_strategies_for_client(client_id: str, symbols: list):
    """
    Entry point to execute multiple registered strategies for a given client.

    This function:
    - Instantiates a StrategyManager
    - Registers multiple strategies (mean reversion + momentum)
    - Runs all strategies across the provided symbols
    - Executes each resulting TradeIntent via run_trade_flow
    - Returns a list of ExecutionContext objects (one per executed trade)

    Args:
        client_id (str): ID of the client to operate on
        symbols (list): List of asset symbols to apply strategies to

    Returns:
        List[ExecutionContext]: Results of executed trades
    """
    # === Step 1: Initialize Strategy Manager for client ===

    # === Step 2: Register available strategy modules ===

    # === Step 3: Run strategies and collect all TradeIntents ===