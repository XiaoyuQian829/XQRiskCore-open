# strategy/strategy_base.py

from core.client_context import ClientContext
from core.trade_intent import TradeIntent
from typing import List


class StrategyModuleBase:
    """
    StrategyModuleBase (Abstract Base Class)
    ========================================
    Base class for all strategy modules. Ensures a consistent interface
    for accessing market data, portfolio state, and generating trade intents.

    Subclasses must implement:
    - generate_trade_intents(symbol: str) -> List[TradeIntent]

    Attributes:
        client_id (str): ID of the client executing this strategy
        ctx (ClientContext): Full client context (portfolio, market, permissions)
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ctx = ClientContext(client_id)  # Provides access to market data, portfolio state, etc.

    def generate_trade_intents(self, symbol: str) -> List[TradeIntent]:
        """
        Abstract method to be implemented by subclasses.

        Given a symbol, return a list of TradeIntent objects representing
        the strategy's recommended trades.

        Args:
            symbol (str): Asset symbol to evaluate (e.g., "AAPL", "SPY")

        Returns:
            List[TradeIntent]: List of trade instructions (can be empty)
        """
        raise NotImplementedError("Subclasses must implement signal logic.")
