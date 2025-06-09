# core/portfolio/asset_position.py

from utils.time_utils import get_timestamps


class AssetPosition:
    """
    AssetPosition
    =============
    Represents a single asset's position state and logic.

    Responsibilities:
    - Track entry, average cost, realized PnL, drawdown, and holding period
    - Handle buy/sell operations and auto-update key metrics
    - Used by portfolio engine for execution, risk attribution, and reporting
    """

    def __init__(self, state: dict):
        # Reference to the asset's mutable state dictionary
        self.state = state

    def record_trade(self, action: str, quantity: int, price: float):
        """
        Apply a buy or sell trade to this asset and update internal state.

        Args:
            action (str): "buy" or "sell"
            quantity (int): Number of shares/contracts traded
            price (float): Executed price (with slippage if applicable)
        """
        now = get_timestamps()["now_ny"].isoformat()
        pos = self.state.get("position", 0)
        avg_price = self.state.get("avg_price", 0.0)

        if action == "buy":
            self._handle_buy(pos, avg_price, quantity, price, now)
        elif action == "sell":
            self._handle_sell(pos, avg_price, quantity, price, now)
        else:
            raise ValueError(f"Unknown action: {action}")

        # Update last trade timestamp
        self.state["last_trade_time"] = now

        # Recalculate drawdown based on current price vs. average cost
        self._update_drawdown()

    def _handle_buy(self, pos: int, avg_price: float, quantity: int, price: float, now: str):
        """
        Process a buy operation and update position, average cost, and entry metadata.
        """
        if pos == 0:
            self.state["entry_time"] = now
            self.state["lowest_price_since_entry"] = price
            self.state["holding_days"] = 1
        else:
            self.state["holding_days"] += 1

        total_cost = avg_price * pos + price * quantity
        new_pos = pos + quantity
        new_avg = total_cost / new_pos if new_pos > 0 else price

        self.state["position"] = new_pos
        self.state["avg_price"] = round(new_avg, 4)
        self.state["lowest_price_since_entry"] = min(
            self.state.get("lowest_price_since_entry", price), price)
        self.state["last_realized_pnl"] = 0.0  # No realized PnL on buy

    def _handle_sell(self, pos: int, avg_price: float, quantity: int, price: float, now: str):
        """
        Process a sell operation and update position, realized PnL, and reset if fully exited.
        """
        if quantity > pos:
            raise ValueError("Cannot sell more than current position")

        realized_pnl = round((price - avg_price) * quantity, 4)
        new_pos = pos - quantity

        self.state["position"] = new_pos
        self.state["last_realized_pnl"] = realized_pnl
        self.state["total_realized_pnl"] = self.state.get("total_realized_pnl", 0.0) + realized_pnl

        if new_pos == 0:
            # Fully exited: reset all position-related fields
            self.state["avg_price"] = 0.0
            self.state["lowest_price_since_entry"] = 0.0
            self.state["holding_days"] = 0
            self.state["entry_time"] = None

    def _update_drawdown(self):
        """
        Recalculate drawdown percentage based on current vs. average price.
        """
        price = self.state.get("current_price", 0.0)
        avg_price = self.state.get("avg_price", 0.0)
        if avg_price > 0:
            drawdown = (price - avg_price) / avg_price
        else:
            drawdown = 0.0
        self.state["drawdown_pct"] = round(drawdown, 6)


"""
AssetPosition — Field Definitions & Functional Overview

| Field Name                | Type           | Update Timing             | Description                                                |
|--------------------------|----------------|----------------------------|------------------------------------------------------------|
| `position`               | `int`          | On buy/sell               | Current number of shares held (0 = fully exited)           |
| `avg_price`              | `float`        | On buy / reset on exit    | Average cost of the current position                       |
| `lowest_price_since_entry` | `float`      | Updated after buy, reset on exit | Lowest observed price since position was opened    |
| `current_price`          | `float`        | After every trade         | Most recent trade price, used as current market value      |
| `drawdown_pct`           | `float`        | Recalculated post-trade   | Max drawdown compared to `avg_price` (in %)                |
| `holding_days`           | `int`          | +1 on buy, reset on exit  | Number of trading days the position has been held          |
| `last_realized_pnl`      | `float`        | On sell                   | Realized PnL from the most recent sell                     |
| `total_realized_pnl`     | `float`        | Accumulated on sell       | Cumulative realized profit from all past sales             |
| `entry_time`             | `str` (ISO)    | Set on first buy, cleared on exit | Timestamp when position was first opened         |
| `last_trade_time`        | `str` (ISO)    | Updated on every trade    | Timestamp of the most recent transaction                   |
| `silent_days_left`       | `int`          | Set when asset is locked, reset to 0 when unlocked | Remaining cooldown days, >0 means currently frozen |
| `silent_trigger_reason`  | `str`          | Set when locked           | Reason for silent lock, e.g., "3-day drop", "10% drawdown" |
| `killswitch`             | `bool`         | Controlled by risk engine | True if asset is blocked from trading                      |
| `last_slippage_pct`      | `float`        | Set per trade             | Slippage percentage for the most recent trade              |
"""

