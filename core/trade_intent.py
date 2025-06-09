# core/trade_intent.py

import uuid
from utils.time_utils import get_timestamps


class TradeIntent:
    """
    TradeIntent defines the initial request to perform a trade.

    This is the canonical object used to capture trade instructions — whether they come
    from a manual user action, a quantitative strategy, or a risk-triggered adjustment.
    It includes identity, context, traceability, and placeholders for risk approval results.
    """

    def __repr__(self):
        return f"<TradeIntent {self.action} {self.quantity} {self.symbol} by {self.trader_id}>"


    def __init__(
        self,
        symbol,
        action,
        quantity,
        source_type="manual",   # Origin classification: "manual", "strategy", "risk_adjustment"
        source="user",          # Specific origin (user ID, strategy name, module)
        timestamp=None,         # Timestamp of submission (defaults to now)
        client_id=None,         # Target client portfolio (multi-client support)
        trader_id=None,         # If submitted by a human trader, record ID
        strategy_id=None,       # If from a strategy, identify it
        notes=None              # Optional contextual notes
    ):
        # Unique ID for this intent (used for tracking and audit)
        self.intent_id = str(uuid.uuid4())

        # Core trade instruction
        self.symbol = symbol              # Asset to trade
        self.action = action              # Direction: "buy" or "sell"
        self.quantity = quantity          # Quantity to trade

        # Source context
        self.source_type = source_type    # Type of origin
        self.source = source              # Specific source ID or label
        self.timestamp = timestamp or get_timestamps()["now_ny"]  # Creation time

        # Routing metadata
        self.client_id = client_id        # Which client this trade applies to
        self.trader_id = trader_id        # Optional human trader ID
        self.strategy_id = strategy_id    # Optional strategy ID
        self.notes = notes or ""          # Free-form notes (UI or strategy generated)

        # Risk evaluation & extension fields
        self.approval = None              # RiskEngine response (approved/rejected + signals)
        self.metadata = {}                # Optional extension: scoring, tags, flags, etc.

    def to_dict(self):
        """
        Serialize the intent as a plain dictionary for logging, display, or storage.
        """
        return {
            "intent_id": self.intent_id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "source_type": self.source_type,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "approval": self.approval,
            "metadata": self.metadata,
            "client_id": self.client_id,
            "trader_id": self.trader_id,
            "strategy_id": self.strategy_id,
            "notes": self.notes,
        }

    def __repr__(self):
        """
        Developer-facing summary of the intent for debugging or logging.
        """
        return (
            f"<TradeIntent [{self.source_type.upper()}] {self.symbol} "
            f"{self.action} {self.quantity} @ {self.timestamp}>"
        )
