# core/portfolio/portfolio.py

from core.portfolio.asset_position import AssetPosition
from utils.time_utils import get_timestamps


class Portfolio:
    """
    Portfolio
    =========
    Represents a full account portfolio, including:
    - Asset-level positions and state
    - Cash balance and execution slippage
    - Trade handling and portfolio-level statistics

    Provides a unified interface for trade updates and generating snapshots
    for UI display, logging, or auditing.
    """

    def __init__(self, state: dict):
        # Mutable reference to portfolio_state (shared across system)
        self.state = state

        # Asset positions dictionary: symbol → asset state dict
        self.assets = state.get("assets", {})

        # Available capital (updated after each trade)
        self.cash = state.get("capital", 0.0)

        # Aggregated slippage statistics
        self.slippage_stats = {
            "total_slippage_pct": 0.0,
            "trade_count": 0
        }

    def add_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        slippage_pct: float = 0.001,
        commission: float = 0.0
    ):
        """
        Apply a trade to the portfolio.

        - Creates asset record if missing
        - Adjusts cash balance
        - Updates asset state via AssetPosition
        - Records slippage and commission stats
        """
        # Initialize asset if not present
        if symbol not in self.assets:
            self.assets[symbol] = {
                "position": 0,
                "avg_price": 0.0,
                "lowest_price_since_entry": price,
                "current_price": price,
                "drawdown_pct": 0.0,
                "drawdown_3d": 0.0,
                "holding_days": 0,
                "killswitch": False,
                "silent_days_left": 0,
                "silent_trigger_reason": "",
                "total_realized_pnl": 0.0,
                "last_realized_pnl": 0.0,
                "total_commission": 0.0,
                "entry_time": None,
                "last_trade_time": None,
                "last_slippage_pct": 0.0,
                "prev_price": price,
                "last_price_time": None
            }

        asset = AssetPosition(self.assets[symbol])
        slip = price * slippage_pct
        exec_price = price + slip if action == "buy" else price - slip

        # Update asset position
        asset.record_trade(action, quantity, exec_price)

        # Adjust account cash
        if action == "buy":
            self.cash -= quantity * exec_price + commission
        elif action == "sell":
            self.cash += quantity * exec_price - commission

        # Update asset-level stats
        self.assets[symbol]["current_price"] = exec_price
        self.assets[symbol]["last_slippage_pct"] = round(slippage_pct * 100, 4)

        self.state["capital"] = round(self.cash, 2)
        self.state["assets"] = self.assets

        # Accumulate slippage stats
        self.slippage_stats["total_slippage_pct"] += abs(slippage_pct * 100)
        self.slippage_stats["trade_count"] += 1

        # Accumulate commission stats
        perf = self.state.setdefault("performance", {})
        perf["total_commission"] = perf.get("total_commission", 0.0) + round(commission, 4)
        self.assets[symbol]["total_commission"] = self.assets[symbol].get("total_commission", 0.0) + round(commission, 4)

        # Debug log (optional for audit)
        print(f"[TRADE] {action.upper()} {quantity} {symbol} @ {exec_price:.2f} (slip: {slippage_pct:.2%})")
        print(f"        Cash: ${self.cash:.2f} | Position: {self.assets[symbol]['position']} | Avg Price: {self.assets[symbol]['avg_price']}")
        print(f"        Realized PnL: {self.assets[symbol]['last_realized_pnl']} | Total: {self.assets[symbol]['total_realized_pnl']}")
        print(f"        Asset Commission: ${self.assets[symbol]['total_commission']} | Account Total Commission: ${perf['total_commission']}")
        print("-" * 60)

    def to_snapshot(self) -> dict:
        """
        Return a standardized snapshot of the portfolio state.

        Includes:
        - Timestamp
        - Capital and net value
        - Per-asset metrics
        - Slippage and commission stats
        """
        avg_slip = (
            self.slippage_stats["total_slippage_pct"] / self.slippage_stats["trade_count"]
            if self.slippage_stats["trade_count"] > 0 else 0.0
        )

        snapshot = {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "capital": round(self.cash, 2),
            "assets": {},
            "net_value": round(
                self.cash + sum(
                    info["position"] * info.get("current_price", 0.0)
                    for info in self.assets.values()
                ), 2),
            "performance": {
                "total_commission": round(self.state.get("performance", {}).get("total_commission", 0.0), 4),
                "slippage": {
                    "total_pct": round(self.slippage_stats["total_slippage_pct"], 4),
                    "avg_pct": round(avg_slip, 4),
                    "trades": self.slippage_stats["trade_count"]
                }
            }
        }

        # Add per-asset stats
        for symbol, info in self.assets.items():
            snapshot["assets"][symbol] = {
                "position": info.get("position", 0),
                "avg_price": info.get("avg_price", 0.0),
                "current_price": info.get("current_price", 0.0),
                "drawdown_pct": info.get("drawdown_pct", 0.0),
                "holding_days": info.get("holding_days", 0),
                "killswitch": info.get("killswitch", False),
                "silent_days_left": info.get("silent_days_left", 0),
                "last_slippage_pct": info.get("last_slippage_pct", 0.0),
                "entry_time": info.get("entry_time", None),
                "last_trade_time": info.get("last_trade_time", None),
                "total_realized_pnl": info.get("total_realized_pnl", 0.0),
                "last_realized_pnl": info.get("last_realized_pnl", 0.0),
                "total_commission": info.get("total_commission", 0.0)
            }

        return snapshot

    def to_dict(self):
        """
        Return the raw portfolio state dictionary.
        Used for saving state to disk or integration with other modules.
        """
        return self.state
# core/portfolio/portfolio.py

from core.portfolio.asset_position import AssetPosition
from utils.time_utils import get_timestamps


class Portfolio:
    """
    Portfolio
    =========
    Represents a full account portfolio, including:
    - Asset-level positions and state
    - Cash balance and execution slippage
    - Trade handling and portfolio-level statistics

    Provides a unified interface for trade updates and generating snapshots
    for UI display, logging, or auditing.
    """

    def __init__(self, state: dict):
        # Mutable reference to portfolio_state (shared across system)
        self.state = state

        # Asset positions dictionary: symbol → asset state dict
        self.assets = state.get("assets", {})

        # Available capital (updated after each trade)
        self.cash = state.get("capital", 0.0)

        # Aggregated slippage statistics
        self.slippage_stats = {
            "total_slippage_pct": 0.0,
            "trade_count": 0
        }

    def add_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        slippage_pct: float = 0.001,
        commission: float = 0.0
    ):
        """
        Apply a trade to the portfolio.

        - Creates asset record if missing
        - Adjusts cash balance
        - Updates asset state via AssetPosition
        - Records slippage and commission stats
        """
        # Initialize asset if not present
        if symbol not in self.assets:
            self.assets[symbol] = {
                "position": 0,
                "avg_price": 0.0,
                "lowest_price_since_entry": price,
                "current_price": price,
                "drawdown_pct": 0.0,
                "drawdown_3d": 0.0,
                "holding_days": 0,
                "killswitch": False,
                "silent_days_left": 0,
                "silent_trigger_reason": "",
                "total_realized_pnl": 0.0,
                "last_realized_pnl": 0.0,
                "total_commission": 0.0,
                "entry_time": None,
                "last_trade_time": None,
                "last_slippage_pct": 0.0,
                "prev_price": price,
                "last_price_time": None
            }

        asset = AssetPosition(self.assets[symbol])
        slip = price * slippage_pct
        exec_price = price + slip if action == "buy" else price - slip

        # Update asset position
        asset.record_trade(action, quantity, exec_price)

        # Adjust account cash
        if action == "buy":
            self.cash -= quantity * exec_price + commission
        elif action == "sell":
            self.cash += quantity * exec_price - commission

        # Update asset-level stats
        self.assets[symbol]["current_price"] = exec_price
        self.assets[symbol]["last_slippage_pct"] = round(slippage_pct * 100, 4)

        self.state["capital"] = round(self.cash, 2)
        self.state["assets"] = self.assets

        # Accumulate slippage stats
        self.slippage_stats["total_slippage_pct"] += abs(slippage_pct * 100)
        self.slippage_stats["trade_count"] += 1

        # Accumulate commission stats
        perf = self.state.setdefault("performance", {})
        perf["total_commission"] = perf.get("total_commission", 0.0) + round(commission, 4)
        self.assets[symbol]["total_commission"] = self.assets[symbol].get("total_commission", 0.0) + round(commission, 4)

        # Debug log (optional for audit)
        print(f"[TRADE] {action.upper()} {quantity} {symbol} @ {exec_price:.2f} (slip: {slippage_pct:.2%})")
        print(f"        Cash: ${self.cash:.2f} | Position: {self.assets[symbol]['position']} | Avg Price: {self.assets[symbol]['avg_price']}")
        print(f"        Realized PnL: {self.assets[symbol]['last_realized_pnl']} | Total: {self.assets[symbol]['total_realized_pnl']}")
        print(f"        Asset Commission: ${self.assets[symbol]['total_commission']} | Account Total Commission: ${perf['total_commission']}")
        print("-" * 60)

    def to_snapshot(self) -> dict:
        """
        Return a standardized snapshot of the portfolio state.

        Includes:
        - Timestamp
        - Capital and net value
        - Per-asset metrics
        - Slippage and commission stats
        """
        avg_slip = (
            self.slippage_stats["total_slippage_pct"] / self.slippage_stats["trade_count"]
            if self.slippage_stats["trade_count"] > 0 else 0.0
        )

        snapshot = {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "capital": round(self.cash, 2),
            "assets": {},
            "net_value": round(
                self.cash + sum(
                    info["position"] * info.get("current_price", 0.0)
                    for info in self.assets.values()
                ), 2),
            "performance": {
                "total_commission": round(self.state.get("performance", {}).get("total_commission", 0.0), 4),
                "slippage": {
                    "total_pct": round(self.slippage_stats["total_slippage_pct"], 4),
                    "avg_pct": round(avg_slip, 4),
                    "trades": self.slippage_stats["trade_count"]
                }
            }
        }

        # Add per-asset stats
        for symbol, info in self.assets.items():
            snapshot["assets"][symbol] = {
                "position": info.get("position", 0),
                "avg_price": info.get("avg_price", 0.0),
                "current_price": info.get("current_price", 0.0),
                "drawdown_pct": info.get("drawdown_pct", 0.0),
                "holding_days": info.get("holding_days", 0),
                "killswitch": info.get("killswitch", False),
                "silent_days_left": info.get("silent_days_left", 0),
                "last_slippage_pct": info.get("last_slippage_pct", 0.0),
                "entry_time": info.get("entry_time", None),
                "last_trade_time": info.get("last_trade_time", None),
                "total_realized_pnl": info.get("total_realized_pnl", 0.0),
                "last_realized_pnl": info.get("last_realized_pnl", 0.0),
                "total_commission": info.get("total_commission", 0.0)
            }

        return snapshot

    def to_dict(self):
        """
        Return the raw portfolio state dictionary.
        Used for saving state to disk or integration with other modules.
        """
        return self.state
# core/portfolio/portfolio.py

from core.portfolio.asset_position import AssetPosition
from utils.time_utils import get_timestamps


class Portfolio:
    """
    Portfolio
    =========
    Represents a full account portfolio, including:
    - Asset-level positions and state
    - Cash balance and execution slippage
    - Trade handling and portfolio-level statistics

    Provides a unified interface for trade updates and generating snapshots
    for UI display, logging, or auditing.
    """

    def __init__(self, state: dict):
        # Mutable reference to portfolio_state (shared across system)
        self.state = state

        # Asset positions dictionary: symbol → asset state dict
        self.assets = state.get("assets", {})

        # Available capital (updated after each trade)
        self.cash = state.get("capital", 0.0)

        # Aggregated slippage statistics
        self.slippage_stats = {
            "total_slippage_pct": 0.0,
            "trade_count": 0
        }

    def add_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        slippage_pct: float = 0.001,
        commission: float = 0.0
    ):
        """
        Apply a trade to the portfolio.

        - Creates asset record if missing
        - Adjusts cash balance
        - Updates asset state via AssetPosition
        - Records slippage and commission stats
        """
        # Initialize asset if not present
        if symbol not in self.assets:
            self.assets[symbol] = {
                "position": 0,
                "avg_price": 0.0,
                "lowest_price_since_entry": price,
                "current_price": price,
                "drawdown_pct": 0.0,
                "drawdown_3d": 0.0,
                "holding_days": 0,
                "killswitch": False,
                "silent_days_left": 0,
                "silent_trigger_reason": "",
                "total_realized_pnl": 0.0,
                "last_realized_pnl": 0.0,
                "total_commission": 0.0,
                "entry_time": None,
                "last_trade_time": None,
                "last_slippage_pct": 0.0,
                "prev_price": price,
                "last_price_time": None
            }

        asset = AssetPosition(self.assets[symbol])
        slip = price * slippage_pct
        exec_price = price + slip if action == "buy" else price - slip

        # Update asset position
        asset.record_trade(action, quantity, exec_price)

        # Adjust account cash
        if action == "buy":
            self.cash -= quantity * exec_price + commission
        elif action == "sell":
            self.cash += quantity * exec_price - commission

        # Update asset-level stats
        self.assets[symbol]["current_price"] = exec_price
        self.assets[symbol]["last_slippage_pct"] = round(slippage_pct * 100, 4)

        self.state["capital"] = round(self.cash, 2)
        self.state["assets"] = self.assets

        # Accumulate slippage stats
        self.slippage_stats["total_slippage_pct"] += abs(slippage_pct * 100)
        self.slippage_stats["trade_count"] += 1

        # Accumulate commission stats
        perf = self.state.setdefault("performance", {})
        perf["total_commission"] = perf.get("total_commission", 0.0) + round(commission, 4)
        self.assets[symbol]["total_commission"] = self.assets[symbol].get("total_commission", 0.0) + round(commission, 4)

        # Debug log (optional for audit)
        print(f"[TRADE] {action.upper()} {quantity} {symbol} @ {exec_price:.2f} (slip: {slippage_pct:.2%})")
        print(f"        Cash: ${self.cash:.2f} | Position: {self.assets[symbol]['position']} | Avg Price: {self.assets[symbol]['avg_price']}")
        print(f"        Realized PnL: {self.assets[symbol]['last_realized_pnl']} | Total: {self.assets[symbol]['total_realized_pnl']}")
        print(f"        Asset Commission: ${self.assets[symbol]['total_commission']} | Account Total Commission: ${perf['total_commission']}")
        print("-" * 60)

    def to_snapshot(self) -> dict:
        """
        Return a standardized snapshot of the portfolio state.

        Includes:
        - Timestamp
        - Capital and net value
        - Per-asset metrics
        - Slippage and commission stats
        """
        avg_slip = (
            self.slippage_stats["total_slippage_pct"] / self.slippage_stats["trade_count"]
            if self.slippage_stats["trade_count"] > 0 else 0.0
        )

        snapshot = {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "capital": round(self.cash, 2),
            "assets": {},
            "net_value": round(
                self.cash + sum(
                    info["position"] * info.get("current_price", 0.0)
                    for info in self.assets.values()
                ), 2),
            "performance": {
                "total_commission": round(self.state.get("performance", {}).get("total_commission", 0.0), 4),
                "slippage": {
                    "total_pct": round(self.slippage_stats["total_slippage_pct"], 4),
                    "avg_pct": round(avg_slip, 4),
                    "trades": self.slippage_stats["trade_count"]
                }
            }
        }

        # Add per-asset stats
        for symbol, info in self.assets.items():
            snapshot["assets"][symbol] = {
                "position": info.get("position", 0),
                "avg_price": info.get("avg_price", 0.0),
                "current_price": info.get("current_price", 0.0),
                "drawdown_pct": info.get("drawdown_pct", 0.0),
                "holding_days": info.get("holding_days", 0),
                "killswitch": info.get("killswitch", False),
                "silent_days_left": info.get("silent_days_left", 0),
                "last_slippage_pct": info.get("last_slippage_pct", 0.0),
                "entry_time": info.get("entry_time", None),
                "last_trade_time": info.get("last_trade_time", None),
                "total_realized_pnl": info.get("total_realized_pnl", 0.0),
                "last_realized_pnl": info.get("last_realized_pnl", 0.0),
                "total_commission": info.get("total_commission", 0.0)
            }

        return snapshot

    def to_dict(self):
        """
        Return the raw portfolio state dictionary.
        Used for saving state to disk or integration with other modules.
        """
        return self.state


