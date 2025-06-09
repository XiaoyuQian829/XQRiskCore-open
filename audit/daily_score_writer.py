# audit/daily_score_writer.py

import os
import json
from datetime import datetime

def write_daily_score(client_id: str, date: str, state: dict):
    """
    Write daily strategy performance score.  
    Structure: audit/strategy_scores/{client_id}/{YYYY-MM-DD}.json

    Parameters:
        - client_id: Client ID  
        - date: Date string (YYYY-MM-DD)  
        - state: Full portfolio state (including performance and risk data)  
    """

    score_dir = f"audit/strategy_scores/{client_id}"
    os.makedirs(score_dir, exist_ok=True)

    score_path = os.path.join(score_dir, f"{date}.json")

    performance = state.get("performance", {})
    score_data = {
        "net_value": state.get("current_net_value", 1.0),
        "daily_return": performance.get("daily_pnl", [])[-1] if performance.get("daily_pnl") else 0.0,
        "monthly_return": performance.get("monthly_pnl", 0.0),
        "silent_mode_days_left": state.get("silent_mode_days_left", 0),
        "triggered_assets": [
            sym for sym, asset in state.get("assets", {}).items()
            if asset.get("silent_days_left", 0) > 0
        ],
        "timestamp": datetime.now().isoformat()
    }

    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)

    print(f"📊 [DailyScoreWriter] Saved daily score → {score_path}")


