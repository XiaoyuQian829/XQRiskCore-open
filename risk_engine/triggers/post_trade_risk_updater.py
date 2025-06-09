# risk_engine/triggers/post_trade_risk_updater.py

class PostTradeRiskUpdater:
    """
    PostTradeRiskUpdater
    ---------------------
    This module is called immediately after a trade is executed.

    It performs post-trade risk updates to ensure the portfolio’s state
    remains coherent and auditable.

    Responsibilities:
    - Re-evaluates portfolio-level risk metrics (e.g. volatility, VaR, CVaR)
    - Updates peak net value if a new high is reached (for drawdown tracking)
    - Initializes asset-level reference points like entry price and max price since entry
    - Ensures consistency for subsequent risk analysis
    """

    def __init__(self, client):
        self.client = client
        self.logger = client.logger  # ✅ Assumes AuditLogger is already attached to client

    def run(self):
        try:
            # 1. Recompute portfolio-level risk metrics
            self.client.risk.evaluate_portfolio_risk()

            # 2. Update account-level peak net value if new high reached
            current_nv = self.client.portfolio.state.get("current_net_value", 0)
            peak_nv = self.client.portfolio.state.get("account_peak_value", current_nv)
            if current_nv > peak_nv:
                self.client.portfolio.state["account_peak_value"] = current_nv

            # 3. Initialize entry and max price for currently held positions
            for symbol, asset in self.client.portfolio.state.get("assets", {}).items():
                if asset.get("position", 0) > 0:
                    entry_price = asset.get("current_price") or asset.get("avg_price")
                    asset["entry_price"] = entry_price
                    asset["max_price_since_entry"] = entry_price

            print(f"[PostTradeRiskUpdater] ✅ Post-trade checks completed for {self.client.client_id}")

        except Exception as e:
            print(f"[PostTradeRiskUpdater] ❌ Failed for {self.client.client_id}: {e}")
