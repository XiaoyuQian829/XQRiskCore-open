# audit/report_generator.py

import json
from pathlib import Path
from utils.time_utils import get_timestamps

def write_strategy_score(client_id: str, state: dict):
    """
    Write daily strategy performance score to audit logs.
    Output path: audit/strategy_scores/{client_id}/{YYYY-MM-DD}.json

    Args:
        client_id (str): Unique identifier for the client
        state (dict): Full portfolio state including performance and risk metrics
    """
    ts = get_timestamps()
    date_str = ts["date_str"]
    path = Path(f"audit/strategy_scores/{client_id}/{date_str}.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    print(f"[✅] Strategy score written to: {path}")
