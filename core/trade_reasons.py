# core/trade_reasons.py

from enum import Enum

class TradeRejectionReason(Enum):
    """
    TradeRejectionReason defines a standardized set of rejection categories
    for failed trade intents.
    """

    SILENT_MODE = "Triggered silent mode"
    LOW_SCORE = "Risk score too low"
    VOL_EXCEED = "Volatility limit exceeded"
    VAR_VIOLATION = "VaR threshold breached"
    MAX_LOSS_EXCEED = "Max allowed loss exceeded"
    KILLSWITCH = "Killswitch enforced"
    INSUFFICIENT_CASH = "Not enough capital"
    DUPLICATE_INTENT = "Duplicate trade intent"
    COOLDOWN_ACTIVE = "Cooling-off period active"
    UNAUTHORIZED = "User not permitted to trade this asset"
    MARKET_CLOSED = "Market is closed"
    STRATEGY_THROTTLED = "Strategy trigger throttled"
    POSITION_TOO_SMALL = "Sell quantity exceeds current position"
    UNKNOWN = "Other or unclassified reason"

    @classmethod
    def match_reason(cls, reason: str):
        reason = reason.lower()

        if "silent" in reason:
            return cls.SILENT_MODE
        elif "score" in reason:
            return cls.LOW_SCORE
        elif "vol" in reason:
            return cls.VOL_EXCEED
        elif "var" in reason:
            return cls.VAR_VIOLATION
        elif "loss" in reason:
            return cls.MAX_LOSS_EXCEED
        elif "kill" in reason:
            return cls.KILLSWITCH
        elif "cash" in reason or "capital" in reason:
            return cls.INSUFFICIENT_CASH
        elif "duplicate" in reason:
            return cls.DUPLICATE_INTENT
        elif "cool" in reason:
            return cls.COOLDOWN_ACTIVE
        elif "unauth" in reason or "permission" in reason:
            return cls.UNAUTHORIZED
        elif "closed" in reason:
            return cls.MARKET_CLOSED
        elif "throttle" in reason:
            return cls.STRATEGY_THROTTLED
        elif "position" in reason or "sell quantity" in reason:
            return cls.POSITION_TOO_SMALL
        else:
            return cls.UNKNOWN


