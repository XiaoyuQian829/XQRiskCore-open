# core/trade_lifecycle.py

from enum import Enum

class TradeLifecycleState(Enum):
    """
    TradeLifecycleState defines all valid end-states for a trade,
    as it passes through the approval, execution, and post-trade audit system.
    """

    INIT = "init"                              # Trade intent created, not yet reviewed
    APPROVED = "approved"                      # Passed risk check, pending execution
    EXECUTED = "executed"                      # Trade successfully placed
    EXECUTED_AUDIT_FAILED = "executed_audit_failed"  # Trade executed, but post-trade audit failed
    REJECTED = "rejected"                      # Rejected by risk engine
    BLOCKED = "blocked"                        # Blocked by silent mode or kill switch
    ERROR = "error"                            # Execution failed due to technical issue
    CANCELLED = "cancelled"                    # Trade was withdrawn before execution
    SKIPPED = "skipped"                        # System skipped trade due to market or config
    TIMEOUT = "timeout"                        # Trade stalled and expired without resolution
    HELD = "held"                              # Manually or automatically deferred (cooling-off)

    def to_status_code(self):
        return {
            TradeLifecycleState.INIT: "INTENT_INIT",
            TradeLifecycleState.APPROVED: "APPROVED",
            TradeLifecycleState.EXECUTED: "EXEC_OK",
            TradeLifecycleState.EXECUTED_AUDIT_FAILED: "EXEC_AUDIT_FAIL",
            TradeLifecycleState.REJECTED: "REJ_GENERAL",
            TradeLifecycleState.BLOCKED: "REJ_SILENT_MODE",
            TradeLifecycleState.ERROR: "EXEC_ERROR",
            TradeLifecycleState.CANCELLED: "CANCELLED",
            TradeLifecycleState.SKIPPED: "SKIPPED",
            TradeLifecycleState.TIMEOUT: "TIMEOUT",
            TradeLifecycleState.HELD: "HELD"
        }.get(self, "UNKNOWN")
