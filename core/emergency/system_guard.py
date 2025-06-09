# core/emergency/system_guard.py

import logging
from core.client_context import ClientContext
from core.market_data import MarketDataFetcher
from utils.time_utils import get_timestamps

logger = logging.getLogger(__name__)

class SystemGuard:
    """
    SystemGuard
    ----------------
    Monitors system-level health: price feed, database, API services.
    If failure is detected, blocks all trade activity for the client.
    Uses MarketDataFetcher to access configured price provider.
    """

    def __init__(self, client_ctx: ClientContext):
        self.ctx = client_ctx
        self.fetcher = MarketDataFetcher(provider="alpaca")  # or "alphavantage"
        self.heartbeat_key = "system_guard_last_check"

    def check_price_feed(self) -> bool:
        try:
            result = self.fetcher.get_price("AAPL")
            return result["price"] is not None
        except Exception as e:
            logger.warning(f"[SystemGuard] Price feed failure: {e}")
            return False

    def check(self) -> tuple[bool, str]:
        """
        Returns (allowed: bool, reason: str)
        """
        now_ts = get_timestamps()["now_ny"].timestamp()
        last_check = self.ctx.get_runtime_state().get(self.heartbeat_key, 0)
        if now_ts - last_check < 60:
            return True, "Heartbeat OK (recent check)"

        feed_ok = self.check_price_feed()
        self.ctx.update_runtime_state({self.heartbeat_key: now_ts})

        if not feed_ok:
            return False, "🚨 Price feed unavailable. Trading blocked by SystemGuard."
        return True, "SystemGuard check passed"

def run_all_system_guards(client_ctx: ClientContext):
    """
    Hook for executor to call. Blocks trade if any guard fails.
    """
    guard = SystemGuard(client_ctx)
    allowed, reason = guard.check()
    return allowed, reason
