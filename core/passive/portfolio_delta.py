# core/passive/portfolio_delta.py

from dataclasses import dataclass
from typing import Dict, List
from utils.config_loader import ConfigLoader


@dataclass
class ExposureDelta:
    """
    Data structure representing the rebalancing instruction for a single asset.
    """
    symbol: str
    target_weight: float
    current_value: float
    target_value: float
    delta_value: float
    current_price: float
    quantity: int
    action: str  # "buy", "sell", "hold"

    def to_dict(self):
        """
        Convert the delta object into a dictionary format, rounding for readability.
        """
        return {
            "symbol": self.symbol,
            "target_weight": round(self.target_weight, 4),
            "current_value": round(self.current_value, 2),
            "target_value": round(self.target_value, 2),
            "delta_value": round(self.delta_value, 2),
            "current_price": round(self.current_price, 2),
            "quantity": self.quantity,
            "action": self.action
        }

    def is_actionable(self) -> bool:
        """
        Determine whether this delta should result in a trade.
        Only BUY or SELL with quantity > 0 are actionable.
        """
        return self.action in ["buy", "sell"] and self.quantity > 0


def compute_portfolio_delta(client_id: str, target_weights: Dict[str, float]) -> List[ExposureDelta]:
    """
    Passive rebalancing engine.

    Compares the client's current portfolio against a target weight allocation
    and computes per-asset trade instructions (buy/sell/hold) based on the difference.

    Args:
        client_id (str): Unique identifier for the client
        target_weights (dict): Mapping of asset symbols to target portfolio weights (0.0–1.0)

    Returns:
        List[ExposureDelta]: Rebalancing actions for each relevant asset
    """
    loader = ConfigLoader(client_id)
    assets = loader.portfolio_state.get("assets", {})
    capital = loader.portfolio_state.get("capital", 0.0)

    current_value_map = {}
    net_value = capital  # Start with cash; will add asset values next

    # Step 1: Calculate current market value of each held asset
    for symbol, info in assets.items():
        pos = info.get("position", 0)
        price = info.get("current_price", 0)
        value = pos * price
        current_value_map[symbol] = {"position": pos, "price": price, "value": value}
        net_value += value

    deltas = []

    # Step 2: For each target-weighted symbol, compute rebalancing difference
    for symbol, target_weight in target_weights.items():
        target_value = target_weight * net_value

        current = current_value_map.get(symbol, {"position": 0, "price": 0.0, "value": 0.0})
        current_value = current["value"]
        current_price = current["price"]

        delta_value = target_value - current_value
        quantity = int(abs(delta_value) // current_price) if current_price > 0 else 0
        action = "buy" if delta_value > 0 else ("sell" if delta_value < 0 else "hold")

        delta = ExposureDelta(
            symbol=symbol,
            target_weight=target_weight,
            current_value=current_value,
            target_value=target_value,
            delta_value=delta_value,
            current_price=current_price,
            quantity=quantity,
            action=action
        )
        deltas.append(delta)

    return deltas

