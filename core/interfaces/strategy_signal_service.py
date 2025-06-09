# core/interfaces/strategy_signal_service.py

from strategy.momentum_strategy import generate_signal
from core.intent.trade_intent import TradeIntent

class StrategySignalService:
    """
    StrategySignalService — Abstracted Strategy Signal Interface
    ------------------------------------------------------------
    Provides a standard interface to call a strategy module and retrieve
    trade intents (e.g., for passive rebalancing or signal-based automation).

    This helps decouple strategy generation from execution or risk logic.
    """

    def __init__(self, strategy_func=generate_signal):
        self.strategy_func = strategy_func

    def generate(self, client_id: str) -> list[TradeIntent]:
        """
        Run strategy and return a list of generated TradeIntent objects.

        Args:
            client_id (str): the target client ID for the strategy context

        Returns:
            List[TradeIntent]: trade ideas from strategy layer
        """
        return self.strategy_func(client_id)
