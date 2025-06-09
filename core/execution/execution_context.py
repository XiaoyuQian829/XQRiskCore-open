# core/execution/execution_context.py

import random
from utils.time_utils import get_timestamps
from core.trade_lifecycle import TradeLifecycleState
from core.trade_reasons import TradeRejectionReason
from core.trade_intent import TradeIntent
from risk_engine.signals.risk_signals import RiskSignalSet


class ExecutionContext:
    """
    ExecutionContext serves as the runtime container for a single trade lifecycle.

    It captures:
    - The original trade intent
    - The risk signals and evaluation context
    - The executor that processed the trade
    - The final execution result (status, price, reason, etc.)
    - Detailed timestamped logs for full traceability

    This object becomes the canonical record for downstream logging, auditing, and report generation.
    """

    def __init__(self, client, intent: TradeIntent, signals: RiskSignalSet, executor_type: str = "unknown"):
        self.client = client                          # ClientContext instance for this trade
        self.intent = intent                          # TradeIntent object (user or strategy origin)
        self.signals = signals                        # Risk evaluation result (score, tags, constraints)
        self.executor_type = executor_type            # Source of execution (manual, strategy, passive)
        self.result = {}                              # Final outcome after execution
        self.logs = []                                # Internal trace log during execution
        self.now = get_timestamps()["now_ny"]         # Timestamp for execution (New York time)

    def record_result(
        self,
        status: str,
        reason: str,
        reason_code: str = None,
        price: float = None,
        expected_price: float = None,
        price_time: str = None,
        slippage_pct: float = None,
        execution_latency_ms: int = None,
        commission: float = 0.0,
        complete: bool = True
    ):
        """
        Record the final result of trade execution.

        This includes execution price, latency, commission, slippage,
        risk approval details, and rejection reason if applicable.
        """
        lifecycle_state = TradeLifecycleState(status)
        reason_enum = TradeRejectionReason.match_reason(reason)

        # Ensure signals are wrapped in RiskSignalSet
        signals_obj = (
            RiskSignalSet.from_dict(self.signals)
            if isinstance(self.signals, dict)
            else self.signals
        )

        self.result = {
            "status": lifecycle_state.value,
            "status_code": lifecycle_state.to_status_code(),
            "reason": reason,
            "reason_code": reason_code or reason_enum.name,
            "price": price,
            "expected_price": expected_price,
            "price_time": price_time,
            "slippage_pct": round(slippage_pct, 4) if isinstance(slippage_pct, (int, float)) else None,
            "execution_latency_ms": execution_latency_ms,
            "commission": commission,
            "timestamp": self.now.isoformat(),
            "signals": signals_obj.to_dict() if signals_obj else {},
            "score": signals_obj.score if signals_obj else None,
            "executor_type": self.executor_type,
            "intent": self.intent.to_dict(),
            "dry_run": self.client.registry_info.get("dry_run", False),
            "broker": self.client.registry_info.get("broker", "unknown"),
            "__complete__": complete
        }

        print(f"[✓] ExecutionContext recorded result: {self.result['status']} | {self.result['reason']}")

    def log(self, message: str, timestamped: bool = True):
        """
        Append a message to the execution log.

        Args:
            message (str): Message to log
            timestamped (bool): If True, prepend current timestamp
        """
        now_str = self.now.isoformat()
        self.logs.append(f"[{now_str}] {message}" if timestamped else message)

    def to_dict(self):
        """
        Export the full execution context as a dictionary.

        Useful for JSON logging, API output, or UI inspection.
        """
        return {
            "intent": self.intent.to_dict(),
            "signals": self.signals.to_dict() if hasattr(self.signals, "to_dict") else {},
            "result": self.result,
            "logs": self.logs
        }

    # --- Convenience properties for status extraction ---

    @property
    def status(self):
        return self.result.get("status")

    @property
    def reason(self):
        return self.result.get("reason")

    @property
    def price(self):
        return self.result.get("price")

    @property
    def score(self):
        return self.result.get("score")

    @property
    def executor_type_str(self):
        return self.result.get("executor_type", self.executor_type or "unknown")

    def to_pretty_log(self) -> str:
        """
        Generate a human-readable summary of the entire trade lifecycle.

        Includes source, trader/strategy metadata, signals, outcome, and execution log.
        """
        i = self.intent
        meta = f"Source: {i.source_type} by {i.source} | Trader: {i.metadata.get('trader_id', 'N/A')} | Strategy: {i.metadata.get('strategy_id', 'N/A')}\n"
        header = f"[{self.executor_type_str}] Intent [{i.intent_id}]: {i.symbol} {i.action} {i.quantity} @ {i.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        signal_str = f"Signals: {self.signals.to_dict()}\n"
        result_str = f"Result: {self.result.get('status')} — Reason: {self.result.get('reason')}\n"
        log_block = "\n".join(self.logs)
        return f"{header}{meta}{signal_str}{result_str}\nLogs:\n{log_block}"

