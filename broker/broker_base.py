# broker/broker_base.py

from abc import ABC, abstractmethod
from typing import Dict

class BrokerInterface(ABC):
    """
    BrokerInterface defines the standard interface for all broker adapters.

    Purpose:
    - Abstract away the differences between broker APIs (e.g., Alpaca, Interactive Brokers)
    - Enable unified trading logic across live, paper, and backtest brokers
    - Serve as the communication layer between the system and external brokers

    Common Use Cases:
    - The execution engine calls `place_order()` without caring about which broker is used
    - Risk or UI modules query current holdings via `get_positions()`
    - Audit logs can include snapshots from `get_account_info()`

    All concrete broker classes must inherit from this interface and implement its methods.
    This ensures consistency, testability, and modular broker integration.
    """

    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """
        Fetch the latest market price for a given asset.

        Args:
            symbol (str): The ticker symbol (e.g., 'AAPL', 'SPY')

        Returns:
            float: Most recent trade price or quote

        Notes:
        - Used for portfolio valuation, trade execution, and risk checks
        - Implementation may use real-time, delayed, or simulated data
        - Concrete classes may implement caching to reduce API calls
        """
        pass

    @abstractmethod
    def place_order(self, symbol: str, quantity: int, action: str) -> Dict:
        """
        Submit a trade order to the broker.

        Args:
            symbol (str): The ticker symbol to trade
            quantity (int): Number of shares or units
            action (str): 'buy' or 'sell'

        Returns:
            Dict: Execution result including status, order ID, fill price, timestamp, etc.

        Notes:
        - The concrete broker must handle order formatting and broker-specific constraints
        - This method may be extended to support limit/market types or stop-loss flags
        - It should return enough metadata for audit logging and post-trade analysis
        """
        pass

    @abstractmethod
    def get_positions(self) -> Dict:
        """
        Retrieve current open positions in the account.

        Returns:
            Dict: A dictionary where each key is a symbol and value is position info

        Example return:
            {
                'AAPL': {'quantity': 100, 'avg_entry_price': 172.3},
                'SPY': {'quantity': 50, 'avg_entry_price': 430.1}
            }

        Notes:
        - Can be used for UI display, portfolio valuation, or strategy allocation logic
        - Must reflect the broker's latest known state
        """
        pass

    @abstractmethod
    def get_account_info(self) -> Dict:
        """
        Fetch account-level information such as total equity, available cash, and margin.

        Returns:
            Dict: Key account metrics from the broker

        Example return:
            {
                'cash': 50000.0,
                'buying_power': 100000.0,
                'equity': 103250.0,
                'maintenance_margin': 25000.0
            }

        Notes:
        - This data supports risk constraints, available capital checks, and dashboard summaries
        - Should be refreshed before any large transaction or margin-sensitive operation
        """
        pass
