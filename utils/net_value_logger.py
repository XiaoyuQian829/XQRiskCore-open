# utils/net_value_logger.py

import os
import json
from datetime import datetime
from typing import Dict, Optional


class NetValueLogger:
    """
    Logger for recording portfolio net value over time as structured JSONL.
    Each line = one daily snapshot.
    """

    def __init__(self, client_id: str, base_path: Optional[str] = None):
        self.client_id = client_id
        self.file_path = self.get_net_value_log_path(base_path)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def get_net_value_log_path(self, base_path: Optional[str] = None) -> str:
        # Resolve full path to net value log file
        if base_path:
            return os.path.join(base_path, "net_value_history.jsonl")
        return os.path.join("clients", self.client_id, "snapshots", "net_value_history.jsonl")

    def file_exists(self) -> bool:
        # Check whether log file exists
        return os.path.exists(self.file_path)

    def append(self, net_value: float, capital: float, positions: Dict[str, dict], reason: str):
        # Append a basic net value snapshot (used in early versions)
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "net_value": round(net_value, 2),
            "capital": round(capital, 2),
            "positions": positions,
            "reason": reason
        }
        with open(self.file_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def append_extended(self, portfolio_state: dict, per_asset_signals: Optional[Dict[str, object]] = None, reason: str = "update"):
        # Append enhanced snapshot, including per-asset positions and optional signal metadata
        date_str = datetime.now().strftime("%Y-%m-%d")
        capital = portfolio_state.get("capital", 0.0)
        net_value = portfolio_state.get("current_net_value", 0.0)
        positions = {}

        for symbol, data in portfolio_state.get("assets", {}).items():
            pos = data.get("position", 0)
            price = data.get("current_price", 0.0)
            if pos == 0:
                continue
            entry = {
                "position": pos,
                "price": price,
                "value": round(pos * price, 2)
            }
            if per_asset_signals and symbol in per_asset_signals:
                signal = per_asset_signals[symbol]
                entry.update(signal.to_dict(extended=True))
            positions[symbol] = entry

        record = {
            "date": date_str,
            "net_value": round(net_value, 2),
            "capital": round(capital, 2),
            "positions": positions,
            "reason": reason
        }

        with open(self.file_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def auto_initialize_if_missing(self, portfolio_state: dict):
        # Auto-log an initial state if file does not exist
        if not self.file_exists():
            print(f"[⚠️] Missing net_value_history.jsonl for {self.client_id}, creating auto-initialization entry...")
            self.append_extended(
                portfolio_state=portfolio_state,
                per_asset_signals={},
                reason="auto-initialization"
            )

    def load_all(self) -> list:
        # Load and return all historical records
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r") as f:
            return [json.loads(line) for line in f if line.strip()]

