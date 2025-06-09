# core/market_data.py

import os
import pandas as pd
import pytz
from datetime import datetime, timedelta
from dotenv import load_dotenv

# External market data providers
from alpha_vantage.timeseries import TimeSeries
from alpaca_trade_api.rest import REST

# Internal utility modules
from utils.asset_utils import get_asset_category
from utils.time_utils import get_timestamps

# Load API keys from .env file for external services
load_dotenv()

# Setup Alpha Vantage (used for daily historical data)
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format='pandas')

# Setup Alpaca (used for real-time quotes and intraday bars)
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
alpaca_api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)


class MarketDataFetcher:
    """
    MarketDataFetcher provides unified access to real-time and historical price data
    from supported providers like Alpaca and Alpha Vantage. It handles live quotes,
    intraday bars, and 100-day daily history with local caching and fallback logic.
    """

    def __init__(self, provider="alphavantage"):
        # Default provider is Alpha Vantage (used for daily price history)
        self.provider = provider

        # Capture current timestamp info for use in data requests
        self.timestamps = get_timestamps()
        self.now_ny = self.timestamps["now_ny"]
        self.today_str = self.timestamps["date_str"]

    def get_price(self, symbol: str) -> dict:
        """
        Fetch the latest market price for a given symbol using Alpaca's live API.

        Args:
            symbol (str): Ticker symbol (e.g., 'AAPL')

        Returns:
            dict: {'price': float or None, 'timestamp': ISO timestamp or None}
        """
        try:
            trade = alpaca_api.get_latest_trade(symbol)
            price = round(trade.price, 2)
            ts_ny = pd.to_datetime(trade.timestamp).tz_convert(self.now_ny.tzinfo).isoformat()
            print(f"{symbol} latest price: {price} @ {ts_ny}")
            return {"price": price, "timestamp": ts_ny}
        except Exception as e:
            print(f"Failed to fetch real-time price for {symbol}: {e}")
            return {"price": None, "timestamp": None}

    def get_intraday(self, symbol: str) -> pd.DataFrame:
        """
        Fetch intraday 5-minute bars using Alpaca's IEX data feed (free tier).

        Args:
            symbol (str): Ticker symbol

        Returns:
            pd.DataFrame: Intraday bar data or empty DataFrame on failure
        """
        try:
            MARKET_TZ = pytz.timezone("America/New_York")
            now = self.now_ny
            today = now.date()

            # Define regular trading hours window for today
            start_dt = datetime(today.year, today.month, today.day, 9, 30, tzinfo=MARKET_TZ)
            end_dt = datetime(today.year, today.month, today.day, 16, 0, tzinfo=MARKET_TZ)

            # If market hasn't opened yet today, fall back to the previous trading day
            if now < start_dt:
                today -= timedelta(days=1)
                start_dt = datetime(today.year, today.month, today.day, 9, 30, tzinfo=MARKET_TZ)
                end_dt = datetime(today.year, today.month, today.day, 16, 0, tzinfo=MARKET_TZ)

            start = start_dt.isoformat(timespec='seconds')
            end = end_dt.isoformat(timespec='seconds')

            bars = alpaca_api.get_bars(
                symbol.upper(),
                "5Min",
                start=start,
                end=end,
                feed="iex"
            ).df

            return bars.reset_index()

        except Exception as e:
            # Fallback for missing Streamlit context or other errors
            print(f"Failed to fetch intraday price for {symbol}: {e}")
            return pd.DataFrame()

    def get_price_history_100d(self, symbol: str) -> pd.DataFrame:
        """
        Fetch 100-day daily price history for a given symbol.

        Uses locally cached data if available. Falls back to Alpha Vantage otherwise,
        and saves the result for future use.

        Args:
            symbol (str): Ticker symbol

        Returns:
            pd.DataFrame: DataFrame with daily OHLCV values or empty on failure
        """
        category = get_asset_category(symbol)
        save_dir = os.path.join("market_data", category.lower(), self.today_str)
        file_name = f"{symbol}_last_100_days.csv"
        save_path = os.path.join(save_dir, file_name)

        if os.path.exists(save_path):
            try:
                print(f"Loading local data for {symbol} from {save_path}")
                return pd.read_csv(save_path)
            except Exception as e:
                print(f"Failed to load local file for {symbol}: {e}, falling back to API")

        try:
            print(f"Fetching daily price data for {symbol} from Alpha Vantage...")
            data, meta = ts.get_daily(symbol=symbol, outputsize='compact')
            df = data.rename(columns={
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. volume": "volume"
            })
            df.index.name = "date"
            df = df.sort_index()
            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize("UTC").tz_convert(self.now_ny.tzinfo)
            df_reset = df.reset_index()

            os.makedirs(save_dir, exist_ok=True)
            df_reset.to_csv(save_path, index=False)
            print(f"{symbol} history saved to {save_path}")
            return df_reset

        except Exception as e:
            print(f"API error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def get_price_history_multi(self, symbols: list) -> dict:
        """
        Fetch 100-day historical price data for multiple symbols.

        Args:
            symbols (list): List of ticker symbols

        Returns:
            dict: Mapping of symbol → DataFrame
        """
        results = {}
        for symbol in symbols:
            df = self.get_price_history_100d(symbol)
            if df is not None and not df.empty:
                results[symbol] = df
        return results

