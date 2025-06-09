# core/passive/risk_signal_factory.py

from typing import Optional
from core.client_context import ClientContext
from risk_engine.signals.risk_signals import RiskSignalSet
import numpy as np


class RiskSignalFactory:
    """
    RiskSignalFactory
    =================
    Generates a RiskSignalSet from portfolio state data.

    This is used in:
    - Passive rebalancing modules
    - Risk-driven asset reallocation
    - Signal pipelines for shutdown logic or score-based exposure shifts
    """

    def __init__(self, client_id: str):
        # Load client context including portfolio state and config
        self.client = ClientContext(client_id)
        self.state = self.client.portfolio_state

    def estimate_volatility(self) -> float:
        """
        Estimate annualized volatility from recent 10-day net value series.
        Can be replaced with a GARCH-based estimator in the future.
        """
        net_values = self.state.get("historical_net_value", [])[-10:]
        if len(net_values) < 2:
            return 0.02  # Fallback: use a median-like conservative estimate

        returns = np.diff(net_values) / net_values[:-1]
        daily_vol = np.std(returns)
        return round(daily_vol * np.sqrt(252), 4)

    def estimate_var(self, confidence=0.95) -> float:
        """
        Estimate Value-at-Risk (VaR) from recent net value changes.
        Returns the 5th percentile of 20-day return distribution by default.
        """
        net_values = self.state.get("historical_net_value", [])[-20:]
        if len(net_values) < 2:
            return -0.02
        returns = np.diff(net_values) / net_values[:-1]
        var = np.percentile(returns, (1 - confidence) * 100)
        return round(var, 4)

    def estimate_cvar(self, confidence=0.95) -> float:
        """
        Estimate Conditional VaR (CVaR) from recent net value history.
        Computes average of returns worse than the VaR threshold.
        """
        net_values = self.state.get("historical_net_value", [])[-20:]
        if len(net_values) < 2:
            return -0.03
        returns = np.diff(net_values) / net_values[:-1]
        threshold = np.percentile(returns, (1 - confidence) * 100)
        cvar = returns[returns <= threshold].mean()
        return round(cvar, 4)

    def build_signal(self, regime: Optional[str] = "Neutral") -> RiskSignalSet:
        """
        Build a RiskSignalSet object from estimated risk indicators.

        Args:
            regime (str): Optional regime label (e.g., "Bull", "Bear", "Neutral")

        Returns:
            RiskSignalSet: Encapsulated scorecard for volatility, VaR, CVaR, and regime
        """
        vol = self.estimate_volatility()
        var = self.estimate_var()
        cvar = self.estimate_cvar()

        signal = RiskSignalSet(
            regime=regime,
            volatility=vol,
            var=var,
            cvar=cvar
        )

        print(f"[RiskSignalFactory] Signal generated: {signal}")
        return signal
