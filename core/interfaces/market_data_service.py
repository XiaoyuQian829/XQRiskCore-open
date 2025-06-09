# core/interfaces/market_data_service.py

from utils.market_data import get_price, get_price_history_100d

class MarketDataService:
    """
    MarketDataService — Abstracted Market Data Access Layer
    --------------------------------------------------------
    Provides unified access to historical and real-time market data.

    This abstraction helps isolate data retrieval logic from strategy,
    risk, or execution layers.
    """

    def __init__(self):
        pass  # Add custom data sources here if needed

    def get_latest_price(self, symbol: str) -> float:
        """
        Fetch the latest available price for the given symbol.

        Args:
            symbol (str): Ticker or instrument ID

        Returns:
            float: Most recent price
        """
        return get_price(symbol)

    def get_recent_history(self, symbol: str) -> list[float]:
        """
        Fetch last 100 trading days of price history.

        Args:
            symbol (str): Ticker or instrument ID

        Returns:
            List[float]: Historical prices
        """
        return get_price_history_100d(symbol)
