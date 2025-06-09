# core/emergency/manager.py

from core.client_context import ClientContext
from core.emergency.system_guard import SystemGuard
from core.emergency.trade_audit_failsafe import TradeAuditFailSafe
from core.emergency.strategy_throttler import StrategyThrottler

def run_emergency_guards(ctx: ClientContext) -> tuple[bool, str]:
    """
    Run all registered emergency guards. Return (allowed: bool, reason: str)
    """
    guards = [
        SystemGuard(ctx),
        StrategyThrottler(ctx),
        # TradeAuditFailSafe intentionally not included here (executed later)
    ]

    for guard in guards:
        allowed, reason = guard.check()
        if not allowed:
            return False, reason

    return True, "✅ All emergency guards passed"