# strategy/strategy_manager.py

from typing import Type, Dict, List
from core.client_context import ClientContext
from core.trade_intent import TradeIntent
from strategy.strategy_base import StrategyModuleBase

class StrategyManager:
    """
    StrategyManager
    ===============
    Central controller for managing and executing multiple strategy modules.

    Responsibilities:
    - Register strategy classes (must inherit from StrategyModuleBase)
    - Instantiate strategies tied to a specific client
    - Invoke all strategies on a given list of symbols
    - Return a unified list of TradeIntent objects

    Attributes:
        client_id (str): The client this strategy manager is operating for
        ctx (ClientContext): Full execution context (portfolio, config, market access)
        strategy_classes (dict): Registered strategy name → class reference
        instances (dict): Instantiated strategies (one per name)
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ctx = ClientContext(client_id)
        self.strategy_classes: Dict[str, Type[StrategyModuleBase]] = {}
        self.instances: Dict[str, StrategyModuleBase] = {}

    def register(self, name: str, strategy_class: Type[StrategyModuleBase]):
        """
        Register a strategy module (must inherit from StrategyModuleBase).

        Args:
            name (str): Unique name to identify the strategy
            strategy_class (Type[StrategyModuleBase]): Class of the strategy

        Raises:
            ValueError: If the class does not inherit from StrategyModuleBase
        """
        if not issubclass(strategy_class, StrategyModuleBase):
            raise ValueError(f"Strategy '{name}' must inherit from StrategyModuleBase")
        self.strategy_classes[name] = strategy_class
        self.instances[name] = strategy_class(self.client_id)

    def run_all(self, symbols: List[str]) -> List[TradeIntent]:
        """
        Run all registered strategies for the given list of symbols.

        Each strategy is responsible for generating intents using its internal logic.

        Args:
            symbols (List[str]): List of asset symbols to evaluate (e.g., ["AAPL", "SPY"])

        Returns:
            List[TradeIntent]: Aggregated trade intents from all strategies
        """
        all_intents = []

        for name, strategy in self.instances.items():
            try:
                for symbol in symbols:
                    intents = strategy.generate_trade_intents(symbol)

                    # Attach source metadata
                    for intent in intents:
                        intent.source_type = "strategy"
                        intent.source = name
                        intent.client_id = self.client_id

                    all_intents.extend(intents)

            except Exception as e:
                print(f"[❌] Strategy '{name}' failed: {e}")

        return all_intents

    def get_client_context(self) -> ClientContext:
        """
        Return the internal ClientContext for direct access if needed.
        """
        return self.ctx
