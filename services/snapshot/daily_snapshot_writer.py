# services/snapshot/daily_snapshot_writer.py

from typing import Dict
from core.client_context import ClientContext
from risk_engine.signals.risk_signals import RiskSignalSet

def run_end_of_day_snapshot(client: ClientContext) -> None:
    per_asset_signals: Dict[str, RiskSignalSet] = {}

    for symbol in client.portfolio_state.get("assets", {}).keys():
        try:
            signal = client.risk.evaluate_daily_risk(symbol)
            if signal:
                per_asset_signals[symbol] = signal
        except Exception as e:
            print(f"[⚠️] Risk evaluation failed for {symbol} — {type(e).__name__}: {e}")

    client.save(
        risk_signals=per_asset_signals,
        reason="end-of-day snapshot"
    )
