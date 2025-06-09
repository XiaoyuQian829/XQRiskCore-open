# risk_engine/daily/state_updater.py

from utils.time_utils import get_timestamps
from datetime import datetime

class DailyStateUpdater:
    """
    DailyStateUpdater
    ==================
    Daily post-market state updater for client portfolios.

    Responsible for:
    - Advancing KillSwitch cooldowns (account & assets)
    - Incrementing `holding_days` and preserving `prev_price`
    - Calculating and recording daily/monthly return rates
    - Resetting `performance` daily fields
    - Logging last update timestamp
    """

    def __init__(self, client):
        self.client = client
        self.state = client.portfolio.state
        self.killswitch = client.killswitch
        self.portfolio = client.portfolio

    def run(self):
        # === Initialize performance block if absent ===
        perf = self.state.setdefault("performance", {})
        current_nv = self.portfolio.estimate_net_value()
        self.state["current_net_value"] = current_nv

        # Set previous day's net value on first use
        if "prev_net_value" not in perf:
            perf["prev_net_value"] = current_nv

        # Set start-of-month value on first use or the 1st day of month
        now = datetime.now()
        if "start_of_month_value" not in perf or now.day == 1:
            perf["start_of_month_value"] = current_nv

        # === Advance cooldown counters via KillSwitch ===
        self.killswitch.daily_tick()

        # === Advance asset-level time fields ===
        for symbol, asset in self.state.get("assets", {}).items():
            # Holding days increment if currently held
            if asset.get("position", 0) > 0:
                asset["holding_days"] = asset.get("holding_days", 0) + 1

            # Store today's price as prev_price for tomorrow
            asset["prev_price"] = asset.get("current_price", 0.0)

        # === Compute return rates ===
        prev_nv = perf.get("prev_net_value", current_nv)
        start_nv = perf.get("start_of_month_value", current_nv)

        daily_ret = (current_nv - prev_nv) / prev_nv if prev_nv else 0.0
        monthly_ret = (current_nv - start_nv) / start_nv if start_nv else 0.0

        perf.setdefault("daily_pnl", []).append(round(daily_ret, 6))
        perf["monthly_pnl"] = round(monthly_ret, 6)
        perf["prev_net_value"] = current_nv  # update reference for next day

        # === Reset intraday closing snapshot container ===
        perf["daily_asset_closes"] = {}

        # === Update portfolio last_updated timestamp ===
        self.state["last_updated"] = get_timestamps()["now_ny"].isoformat()

        # === Optional logging for audit/debugging ===
        print(f"[DailyStateUpdater] ✅ {self.client.client_id} updated.")
        print(f"   📈 Daily Return: {daily_ret:.2%} | Monthly Return: {monthly_ret:.2%}")
