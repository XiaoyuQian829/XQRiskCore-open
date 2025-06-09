# core/passive/rebalance_engine.py

from typing import List
from core.client_context import ClientContext
from risk_engine.signals.risk_signals import RiskSignalSet
from core.passive.exposure_logic import compute_target_exposure
from core.passive.portfolio_delta import compute_portfolio_delta, ExposureDelta
from core.trade_intent import TradeIntent
from core.passive.risk_signal_factory import RiskSignalFactory
from utils.net_value_logger import NetValueLogger
from statistics import mean


def compute_passive_score(net_values: List[float]) -> float:
    """
    Compute a simplified trend score based on net value slope.

    Returns a normalized slope in [-1, 1] using recent NAV data.
    """
    if len(net_values) < 2:
        return 0.0

    x = list(range(len(net_values)))
    y = net_values
    n = len(x)
    avg_x = sum(x) / n
    avg_y = sum(y) / n
    cov = sum((xi - avg_x) * (yi - avg_y) for xi, yi in zip(x, y))
    var = sum((xi - avg_x) ** 2 for xi in x)

    slope = cov / var if var != 0 else 0
    norm_slope = max(min(slope / 50, 1), -1)  # adjustable scaling factor
    return round(norm_slope, 2)


class PassiveRebalancer:
    """
    PassiveRebalancer (under development)

    This class implements passive, risk-driven rebalancing logic based on:
    - Portfolio drawdown
    - Net value trends
    - Risk score from RiskSignalSet

    It computes target weights, detects portfolio deltas,
    and generates corresponding TradeIntent objects.
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ctx = ClientContext(client_id)  # Load full portfolio context
        self.state = self.ctx.portfolio_state
        self.assets = self.state.get("assets", {})
        self.signal: RiskSignalSet = None
        self.target_weights = {}
        self.deltas: list[ExposureDelta] = []
        self.intents: list[TradeIntent] = []

    def should_rebalance(self) -> bool:
        """
        Determine whether passive rebalancing should be triggered.

        Conditions:
        - Downward trend in net value over past 10 days
        - Drawdown exceeds 5%
        - Risk score below a defensive threshold
        """
        log = NetValueLogger(self.client_id)
        records = log.read_recent(10)

        if len(records) < 5:
            return False

        net_values = [r["net_value"] for r in records if "net_value" in r]
        trend = net_values[-1] - net_values[0]

        current_nv = self.state.get("current_net_value", 1.0)
        peak_nv = self.state.get("account_peak_value", current_nv)
        drawdown = (current_nv - peak_nv) / peak_nv

        score = 0.0
        try:
            sample_asset = next(iter(self.assets.keys()), None)
            if sample_asset:
                signal = self.ctx.risk.evaluate_daily_risk(sample_asset)
                score = signal.score
        except:
            pass

        if trend < 0 and drawdown <= -0.05:
            print(f"[Trigger] Rebalance: Trend ↓ {trend:.2f}, Drawdown {drawdown:.2%}, Score {score}")
            return True

        if score < -0.5:
            print(f"[Trigger] Rebalance due to low score = {score}")
            return True

        return False

    def load_risk_signal(self):
        """
        Build a RiskSignalSet from the default signal factory.
        """
        factory = RiskSignalFactory(self.client_id)
        self.signal = factory.build_signal(regime="Neutral")

    def compute_target_weights(self):
        """
        Generate target exposure weights based on the risk signal.
        """
        self.target_weights = compute_target_exposure(self.signal)

    def compute_deltas(self):
        """
        Compare current holdings with target weights to compute deltas.
        """
        self.deltas = compute_portfolio_delta(self.client_id, self.target_weights)

    def build_trade_intents(self):
        """
        Convert each actionable delta into a TradeIntent.
        """
        for delta in self.deltas:
            if not delta.is_actionable():
                continue

            intent = TradeIntent(
                symbol=delta.symbol,
                action=delta.action,
                quantity=delta.quantity,
                source_type="passive_adjustment",
                source="weekly_rebalancer",
                client_id=self.client_id,
                notes=f"Target {delta.target_weight:.1%} exposure from score {self.signal.score}"
            )
            self.intents.append(intent)

    def run(self) -> list[TradeIntent]:
        """
        Main entry point to compute trade intents from risk-adjusted targets.
        """
        self.load_risk_signal()
        self.compute_target_weights()
        self.compute_deltas()
        self.build_trade_intents()
        return self.intents




"""
✅ 3. PassiveRebalancer — Risk-Driven Passive Rebalancing  
📄 Location: core/passive/rebalance_engine.py  
🔧 Does not inherit from strategy base class, but still produces TradeIntent objects  

🎯 Core Concept:
Automatically compute target asset allocations (e.g., SPY/TLT) based on the risk score (`RiskSignalSet.score`),  
then compare with current portfolio weights to generate rebalancing trade intents.

⚙️ Implementation Logic:
Input: System-level risk signals (e.g., regime, GARCH volatility, VaR/CVaR)  
Output: Target weight distribution (e.g., SPY 80%, TLT 20%)  
→ Compare with current positions → Generate buy/sell intents  
→ Execute via PassiveRebalanceExecutor

📌 Characteristics:
Aspect                | Description
--------------------- | -----------------------------------------------
Static weight-driven  | Periodic re-alignment of exposures (e.g., weekly, monthly)  
Risk-oriented         | Lower score → more defensive asset allocation  
Low-frequency         | Designed for ETF/Bond rhythm, not daily noise  
Strategy-decoupled    | Operates independently of alpha signals; adjusts macro exposure only  
"""
