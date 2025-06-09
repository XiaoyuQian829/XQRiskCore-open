# core/interfaces/trade_flow_service.py

from services.trade_flow import run_trade_flow
from core.client_context import ClientContext
from core.intent.trade_intent import TradeIntent
from core.execution.execution_context import ExecutionContext

class TradeFlowService:
    """
    TradeFlowService — Abstracted Trade Lifecycle Interface
    -------------------------------------------------------
    Provides a clean interface to submit and run a full trade lifecycle:
    - Silent scan
    - KillSwitch enforcement
    - Risk approval
    - Execution
    - Post-trade logging and audit

    Used for demo, SDK prototyping, and system abstraction.
    """

    def __init__(self, client_ctx: ClientContext):
        self.ctx = client_ctx

    def submit(self, intent: TradeIntent) -> ExecutionContext:
        """
        Submit a TradeIntent and run the full trade lifecycle.

        Args:
            intent (TradeIntent): structured trade instruction object

        Returns:
            ExecutionContext: result object with trade status and logs
        """
        return run_trade_flow(self.ctx, intent)
