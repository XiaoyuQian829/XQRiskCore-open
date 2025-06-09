# core/interfaces/risk_evaluator_service.py

from risk_engine.controller import RiskController
from core.client_context import ClientContext
from core.intent.trade_intent import TradeIntent
from risk_engine.signals.risk_signals import RiskSignalSet

class RiskEvaluatorService:
    """
    RiskEvaluatorService — Abstracted Risk Approval Interface
    ----------------------------------------------------------
    Provides a clean method to evaluate a TradeIntent against risk rules
    and return structured approval signals.

    This isolates the risk logic for external testing, preview, or SDK use.
    """

    def __init__(self, client_ctx: ClientContext):
        self.controller = RiskController(client_ctx)

    def evaluate(self, intent: TradeIntent) -> RiskSignalSet:
        """
        Run risk evaluation on the given TradeIntent.

        Args:
            intent (TradeIntent): The proposed trade action

        Returns:
            RiskSignalSet: structured risk approval outcome
        """
        return self.controller.evaluate(intent)
