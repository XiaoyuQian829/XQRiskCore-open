# admin/add_client.py

import os
import yaml
import json
from utils.time_utils import get_timestamps

timestamps = get_timestamps()

def create_client_from_config(config: dict):
    client_id = config["client_id"]
    base_path = os.path.join("clients", client_id)

    # === Step 1: Create full directory structure ===
    dirs = [
        "config",
        "snapshots/current",
        "snapshots/archive",
        "audit/decisions",
        "audit/cooling_off_logs",
        "audit/killswitch_logs",
        "audit/daily_summary",
        "audit/periodic_scan_logs",
        "audit/monthly_optimizer",
        "reports/figs",
        "logs"
    ]
    for d in dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)

    # === Step 2: Create asset_config.yaml (final structure) ===
    asset_config = {
        "symbol_universe": config["assets"],
        "risk_style": config["risk_style"],
        "risk_constraints": {
            "max_drawdown_pct": config["max_drawdown_pct"],
            "min_holding_days": config["min_holding_days"],
            "silent_after_loss_days": config["silent_after_loss_days"]
        }
    }
    with open(os.path.join(base_path, "config/asset_config.yaml"), "w") as f:
        yaml.dump(asset_config, f)

    # === Step 3: Create empty portfolio_state.json ===
    base_capital = config["base_capital"]
    assets = config["assets"]

    portfolio = {
        "capital": base_capital,
        "current_net_value": base_capital,
        "account_peak_value": base_capital,
        "assets": {},
        "performance": {
            "daily_pnl": [],
            "daily_asset_closes": {},
            "monthly_pnl": 0.0,
            "prev_net_value": base_capital,
            "start_of_month_value": base_capital,
            "total_commission": 0.0
        },
        "trades": [],
        "silent_mode": False,
        "silent_mode_days_left": 0,
        "silent_reason": "",
        "killswitch_active": False,
        "consecutive_losses": 0,
        "last_drawdown_check": timestamps["now_ny"].isoformat(),
        "last_updated": timestamps["now_ny"].isoformat()
    }

    with open(os.path.join(base_path, "snapshots/current/portfolio_state.json"), "w") as f:
        json.dump(portfolio, f, indent=2)


    history_path = os.path.join(base_path, "snapshots", "net_value_history.jsonl")

    init_record = {
        "date": timestamps["date_str"],
        "net_value": base_capital,
        "capital": base_capital,
        "positions": {}, 
        "reason": "initialization"
    }

    with open(history_path, "a") as f:
        f.write(json.dumps(init_record) + "\n")


    # === Step 4: Register in client_registry.yaml (minimal clean version) ===
    registry_path = "clients/client_registry.yaml"
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = yaml.safe_load(f) or {}
    else:
        registry = {}

    registry[client_id] = {
        "name": config["name"],
        "api_provider": config["api_provider"],
        "api_key": config.get("api_key", ""),
        "dry_run": config["dry_run"],
        "base_capital": config["base_capital"],
        "broker": config["broker"],
        "broker_keys": config.get("broker_keys", {}),
        "enable_intraday_trigger": config.get("enable_intraday_trigger", True),
        "intraday_trigger_interval_minutes": config.get("intraday_trigger_interval_minutes", 10),
        "created_at": timestamps["ny_time_str"]
    }

    with open(registry_path, "w") as f:
        yaml.dump(registry, f, sort_keys=False)

