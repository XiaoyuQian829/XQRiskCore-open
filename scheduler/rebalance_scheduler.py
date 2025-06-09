# scheduler/rebalance_scheduler.py

"""
XQRiskCore - Scheduled Passive Rebalancing Scheduler
====================================================

This module runs **scheduled passive rebalancing** for all clients.

💡 When triggered (typically Fridays or scheduled jobs), it performs:
- Passive risk evaluation for each client
- Rebalancing intent generation if risk posture demands adjustment
- Frequency-based filtering per asset (weekly / biweekly / monthly)
- Execution of trade intents via the standard trade flow pipeline
"""

import datetime
from utils.time_utils import get_timestamps
from utils.asset_utils import get_asset_rebalance_schedule, get_asset_category as get_asset_type
from utils.config_loader import load_client_registry
from core.passive.rebalance_engine import PassiveRebalancer
from services.trade_flow import run_trade_flow
from core.client_context import ClientContext


def is_rebalance_due_today(freq: str, date: datetime.date = None) -> bool:
    """
    Determine if an asset with the given frequency is due for rebalance today.

    Supported frequencies:
    - weekly: every Friday
    - biweekly: every 2nd Friday
    - monthly: first 3 weekdays of each month
    """
    if date is None:
        date = get_timestamps()["now_ny"].date()

    if freq == "weekly":
        return date.weekday() == 4  # Friday

    elif freq == "biweekly":
        return date.isocalendar().week % 2 == 0 and date.weekday() == 4

    elif freq == "monthly":
        return date.day <= 3 and date.weekday() < 5

    return False


def run_scheduled_rebalance(client_id: str):
    """
    Execute passive rebalancing for a single client, if eligible.
    - Step 1: Instantiate rebalancer
    - Step 2: Check whether strategy conditions trigger rebalance
    - Step 3: Filter intents by asset-level rebalance schedule
    - Step 4: Execute filtered trade intents
    """
    print(f"\n🔄 Running passive rebalance for {client_id}")
    rebalancer = PassiveRebalancer(client_id)

    if not rebalancer.should_rebalance():
        print(f"[⏸] Skip {client_id} — Not eligible for passive rebalance today.")
        return

    intents = rebalancer.run()
    today = get_timestamps()["now_ny"].date()
    filtered = []

    for intent in intents:
        freq = get_asset_rebalance_schedule(intent.symbol)
        if is_rebalance_due_today(freq, today):
            filtered.append(intent)
        else:
            print(f"[⏭] Skipped {intent.symbol} — type={get_asset_type(intent.symbol)}, schedule={freq}")

    if not filtered:
        print("✅ No rebalancing due today for this client.")
        return

    ctx = ClientContext(client_id)
    for intent in filtered:
        print(f"⚙️ Executing: {intent.symbol} {intent.action} {intent.quantity}")
        run_trade_flow(ctx, intent)

    print(f"✅ {len(filtered)} passive trades executed for {client_id}.")


def run_all_scheduled_rebalances():
    """
    Run passive rebalancing across all clients.
    This is the entry point for a scheduled daily/weekly job.
    """
    ts = get_timestamps()
    print(f"\n[{ts['ny_time_str']}] 🚀 Starting passive rebalancing for all clients...\n")

    registry = load_client_registry()
    for cid in registry:
        try:
            run_scheduled_rebalance(cid)
        except Exception as e:
            print(f"[❌] Rebalancing failed for {cid} — {type(e).__name__}: {e}")

    print(f"\n[{ts['ny_time_str']}] ✅ Passive rebalancing complete for all clients.\n")


if __name__ == "__main__":
    run_all_scheduled_rebalances()


