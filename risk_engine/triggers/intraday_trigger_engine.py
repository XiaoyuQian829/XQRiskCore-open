# risk_engine/triggers/intraday_trigger_engine.py

"""
IntradayTriggerEngine v2.1 — Real-time Risk Guard
==================================================

This engine monitors live account and asset-level metrics and applies
**Silent Mode lockdowns** when predefined intraday thresholds are breached.

Typical triggers include:
- Portfolio drawdown beyond -5%
- Asset drawdown beyond -7%
- Consecutive down days ≥ 3
- Intraday drop > 8%
- 3-day rolling drawdown > -10%
- Abnormal slippage > 0.5%

⚠️ Source code is withheld for governance and control integrity.  
✅ Production version is fully operational and integrated.
"""

class IntradayTriggerEngine:
    def __init__(self, client):
        """
        Initialize with client state and KillSwitch mechanism.
        """
        self.client = client
        self.state = client.portfolio_state
        self.killswitch = client.killswitch

    def scan_intraday_metrics(self):
        """
        Step 1. Snapshot current risk metrics

        - Account-level:
            - current_net_value
            - peak_value
            - drawdown
            - whether drawdown > -5% and not already under Silent Mode

        - Asset-level:
            For each symbol:
            - current price, avg entry price, previous price
            - drawdown from avg (pos_drawdown)
            - 3-day drawdown (drawdown_3d)
            - slippage percentage
            - consecutive down days

            Flag triggers:
            - drawdown > 7%
            - 3-day down trend
            - intraday price drop > 8%
            - drawdown_3d > 10%
            - slippage > 0.5%

        Returns:
            dict: {
                "account": {...},
                "assets": {
                    symbol: {
                        ...,
                        "triggers": {
                            drawdown: bool,
                            consec_down: bool,
                            intraday_drop: bool,
                            drawdown_3d: bool,
                            slippage: bool
                        }
                    }
                }
            }
        """
        pass  # Source hidden

    def run_intraday(self):
        """
        Step 2. Apply rule-based enforcement

        - If account-level trigger breached:
            → Lock all assets via `trigger_silent_all`

        - If asset-level triggers breached:
            → Lock individual symbols via `trigger_silent`

        - Record silent trigger reasons and source codes:
            - "ACCOUNT_DD_GT_5"
            - "DRAW_POS_GT_7"
            - "CONSEC_DOWN_3D"
            - "DROP_GT_8"
            - "DD3_GT_10"
            - "SLIPPAGE_ANOMALY"

        - Attach snapshot to client (for UI and logs)
        - Print trigger result to console

        Returns:
            dict: Intraday risk snapshot
        """
        pass  # Source hidden


