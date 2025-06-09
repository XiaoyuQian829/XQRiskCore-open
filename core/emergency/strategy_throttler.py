# core/emergency/strategy_throttler.py

from core.client_context import ClientContext
from utils.time_utils import get_timestamps

class StrategyThrottler:
    """
    StrategyThrottler
    -----------------
    Prevents over-frequent or reckless automated strategy submissions.
    Enforces two layers of control:
    - Submission frequency limits
    - Consecutive failure protection
    """

    def __init__(self, ctx: ClientContext):
        self.ctx = ctx
        self.state_key = "strategy_throttle_state"
        self.now = get_timestamps()["now_ny"]

    def check(self) -> tuple[bool, str]:
        """
        Entry point: Check whether the strategy is allowed to proceed.
        
        Returns:
            (allowed: bool, reason: str)
        """
        intent = self.ctx.intent
        if intent.source != "strategy":
            return True, "Not a strategy trade. Throttling not applied."

        # Load or initialize runtime state
        state = self.ctx.get_runtime_state().get(self.state_key, {
            "last_time": None,
            "count": 0,
            "consecutive_failures": 0
        })

        last_time = state["last_time"]
        count = state["count"]
        failures = state["consecutive_failures"]

        now_ts = self.now.timestamp()

        # === Step 1: Limit strategy submissions per minute ===
        if last_time and now_ts - last_time < 60:
            if count >= 5:
                return False, "❌ Strategy throttled: too many submissions within 1 minute."
            else:
                state["count"] += 1
        else:
            state["count"] = 1
            state["last_time"] = now_ts

        # === Step 2: Block after 3 consecutive failures ===
        if failures >= 3:
            return False, "❌ Strategy disabled: 3+ consecutive failures detected."

        # Save updated runtime state
        self.ctx.update_runtime_state({self.state_key: state})
        return True, "✅ Strategy throttle check passed."

    def report_failure(self):
        """
        Call this when a strategy trade fails (e.g. rejected or audit failure).
        Increments the failure counter.
        """
        state = self.ctx.get_runtime_state().get(self.state_key, {
            "consecutive_failures": 0
        })
        state["consecutive_failures"] += 1
        self.ctx.update_runtime_state({self.state_key: state})

    def reset_failure_count(self):
        """
        Call this after a successful strategy trade.
        Resets the failure counter to 0.
        """
        state = self.ctx.get_runtime_state().get(self.state_key, {})
        state["consecutive_failures"] = 0
        self.ctx.update_runtime_state({self.state_key: state})
