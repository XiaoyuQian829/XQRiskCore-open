# core/trade_manager.py

import pandas as pd
from utils.time_utils import get_timestamps
from utils.trade_utils import simulate_slippage


class TradeManager:
    """
    TradeManager manages structured trade records without affecting portfolio state.

    This module maintains a lightweight trade ledger used for:
    - Lifecycle tracking of all trades (open/closed)
    - Post-trade analytics (slippage, drawdown, PnL)
    - Backtest replays, compliance logs, and reporting
    - Stored under portfolio_state["trades"]
    """

    def __init__(self, portfolio_state, client_id=None):
        # Reference to client's portfolio state dict (mutable)
        self.portfolio_state = portfolio_state
        self.client_id = client_id

        # In-memory trade list, persisted in portfolio_state["trades"]
        self.trades = self.portfolio_state.setdefault("trades", [])

    def add_trade(
        self,
        symbol: str,
        action: str,
        executed_price: float,
        position_size: int,
        expected_price: float = None,
        slippage_pct: float = None,
        execution_latency_ms: int = None,
        commission: float = 0.0,
        source: str = "manual",
        intent_id: str = None
    ):
        """
        Add a new trade entry with full execution details.

        This method records metadata such as slippage, latency, commission,
        and associates the trade with a TradeIntent ID.
        """
        now = self._now()
        expected_price = expected_price or executed_price
        slippage_pct = (
            slippage_pct if slippage_pct is not None
            else simulate_slippage(executed_price, expected_price)
        )

        trade = {
            "symbol": symbol,
            "action": action,
            "entry_time": now,
            "entry_price": executed_price,
            "expected_price": expected_price,
            "slippage_pct": round(slippage_pct, 4),
            "execution_latency_ms": execution_latency_ms,
            "commission": round(commission, 4),
            "position_size": position_size,
            "lowest_price_since_entry": executed_price,
            "current_price": executed_price,
            "max_drawdown_pct": 0.0,
            "status": "open",
            "source": source,
            "intent_id": intent_id
        }

        self.trades.append(trade)
        print(f"[TradeManager] Added {action.upper()} {position_size} {symbol} @ {executed_price:.2f}")

    def update_trade(self, symbol: str, current_price: float):
        """
        Update current price and max drawdown for an open trade.

        This is typically called during live valuation or rolling audits.
        """
        for trade in self.trades:
            if trade["symbol"] == symbol and trade["status"] == "open":
                trade["current_price"] = current_price
                if current_price < trade["lowest_price_since_entry"]:
                    trade["lowest_price_since_entry"] = current_price
                drawdown = (trade["lowest_price_since_entry"] - trade["entry_price"]) / trade["entry_price"]
                trade["max_drawdown_pct"] = round(drawdown * 100, 4)
                break

    def check_trade_max_loss(self, symbol: str, account_capital: float, max_loss_pct: float = 1.0) -> bool:
        """
        Check whether an open position has exceeded a maximum loss threshold.

        Returns True if drawdown surpasses the allowed percentage of account capital.
        """
        for trade in self.trades:
            if trade["symbol"] == symbol and trade["status"] == "open":
                loss_amount = (trade["entry_price"] - trade["lowest_price_since_entry"]) * trade["position_size"]
                max_loss_amount = account_capital * max_loss_pct / 100
                return loss_amount >= max_loss_amount
        return False

    def close_trade(self, symbol: str, exit_price: float):
        """
        Close an open trade by marking status and recording exit price/time.

        This does not update positions — only the trade ledger.
        """
        for trade in self.trades:
            if trade["symbol"] == symbol and trade["status"] == "open":
                trade["exit_price"] = exit_price
                trade["exit_time"] = self._now()
                trade["status"] = "closed"
                break

    def get_monthly_summary(self) -> dict:
        """
        Aggregate monthly trade performance.

        Returns a dictionary keyed by 'YYYY-MM' with metrics such as:
        - trade count, win rate, total PnL, drawdown, slippage, commission
        """
        if not self.trades:
            return {}

        df = pd.DataFrame(self.trades)
        if df.empty or "exit_price" not in df.columns:
            return {}

        df["exit_time"] = pd.to_datetime(df["exit_time"])
        df["month"] = df["exit_time"].dt.to_period("M").astype(str)
        df["pnl"] = (df["exit_price"] - df["entry_price"]) * df["position_size"]
        df["win"] = df["pnl"] > 0

        summary = df.groupby("month").agg(
            total_trades=("symbol", "count"),
            wins=("win", "sum"),
            losses=("win", lambda x: (~x).sum()),
            win_rate=("win", lambda x: round(100 * x.sum() / len(x), 1)),
            total_pnl=("pnl", "sum"),
            max_drawdown_pct=("max_drawdown_pct", "max"),
            avg_slippage_pct=("slippage_pct", "mean"),
            avg_commission=("commission", "mean")
        ).to_dict(orient="index")

        return summary

    @staticmethod
    def _now():
        """
        Return the current timestamp in ISO string format (New York timezone).
        """
        return get_timestamps()["now_ny"].isoformat()


"""
| Field Name                | Type    | Source / Meaning                                      | Usage Description                           |
|--------------------------|---------|-------------------------------------------------------|---------------------------------------------|
| `symbol`                 | `str`   | Ticker symbol of the asset (e.g., "AAPL")             | Identifies the traded security              |
| `action`                 | `str`   | Either `"buy"` or `"sell"`                            | Indicates trade direction                   |
| `entry_time`             | `str`   | Timestamp from `get_timestamps()["now_ny"]`           | Entry time, used for daily/monthly grouping |
| `entry_price`            | `float` | Actual execution price (includes slippage)            | Used for PnL, drawdown, and slippage calc   |
| `expected_price`         | `float` | Expected price (e.g., from `get_price()` result)      | Used to compute slippage                    |
| `slippage_pct`           | `float` | Percentage deviation from expected to actual price    | Used for slippage analysis and robustness   |
| `execution_latency_ms`   | `int`   | Time delay from intent to execution (optional)        | For latency profiling or backtest sync      |
| `commission`             | `float` | Commission charged per trade                          | Included in cost analytics                  |
| `position_size`          | `int`   | Number of shares/contracts executed                   | Key to capital usage and exposure sizing    |
| `lowest_price_since_entry` | `float` | Lowest observed price since entry                    | Used to monitor floating loss / drawdown    |
| `current_price`          | `float` | Most recent updated price                             | Used in real-time UI snapshots and audits   |
| `max_drawdown_pct`       | `float` | Maximum drawdown since entry (as % from entry price)  | For risk evaluation, alerts, or stop logic  |
| `status`                 | `str`   | Either `"open"` or `"closed"`                         | Indicates lifecycle state of the trade      |
| `exit_price`             | `float` | Price at which the trade was closed                   | Only present if status is `"closed"`        |
| `exit_time`              | `str`   | Timestamp of trade closure                            | Used in reporting and time-based analytics  |
| `source`                 | `str`   | Source of the trade: `"manual"`, `"strategy"`, etc.   | Differentiates user input, algorithmic, or risk-based |
| `intent_id`              | `str`   | UUID from originating TradeIntent                     | Serves as a cross-system audit anchor       |
"""
