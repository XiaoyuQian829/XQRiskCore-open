# utils/config_loader.py

import os
import json
import shutil
import yaml
from typing import Dict, List, Optional

from utils.net_value_logger import NetValueLogger  # ✅ Structured logger for historical net value tracking

# Default configuration for any new or incomplete client entry
DEFAULT_CLIENT_CONFIG = {
    "name": "Unnamed",
    "api_provider": "alpha_vantage",
    "api_key": "",
    "dry_run": True,
    "base_capital": 100000,
    "broker": "alpaca",
    "broker_keys": {"key": "", "secret": ""},
    "enable_intraday_trigger": True,
    "intraday_trigger_interval_minutes": 10,
    "created_at": ""
}

def save_client_registry(updated_registry):
    """Save the full client registry to YAML."""
    with open("clients/client_registry.yaml", "w") as f:
        yaml.dump(updated_registry, f, sort_keys=False)

def load_client_registry(path="clients/client_registry.yaml") -> dict:
    """
    Load all client entries from the YAML registry.
    Fills in missing fields with DEFAULT_CLIENT_CONFIG.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_path = os.path.join(root_dir, path)

    if not os.path.exists(full_path):
        print(f"⛔ client_registry.yaml not found at: {full_path}")
        return {}

    with open(full_path, "r") as f:
        data = yaml.safe_load(f)
        if not isinstance(data, dict):
            print("⚠️ client_registry.yaml must be a dictionary of clients")
            return {}

    merged = {}
    for client_id, cfg in data.items():
        cfg = cfg or {}
        full_cfg = {**DEFAULT_CLIENT_CONFIG, **cfg}
        merged[client_id] = full_cfg

    return merged

def load_client_asset_config(client_id: str) -> dict:
    """Load per-client asset_config.yaml."""
    path = os.path.join("clients", client_id, "config", "asset_config.yaml")
    if not os.path.exists(path):
        print(f"⚠️ asset_config.yaml not found for client: {client_id}")
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def save_client_asset_config(client_id: str, config: dict):
    """Save per-client asset_config.yaml."""
    path = os.path.join("clients", client_id, "config", "asset_config.yaml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(config, f, sort_keys=False)
    print(f"✅ asset_config.yaml saved for client: {client_id}")

def load_client_entry(client_id: str) -> dict:
    """Load a single client entry from the registry."""
    registry = load_client_registry()
    return registry.get(client_id, DEFAULT_CLIENT_CONFIG.copy())

def get_client_assets(client_id: str) -> List[str]:
    """Shortcut to load tradable symbols for a given client."""
    from utils.config_loader import ConfigLoader
    loader = ConfigLoader(client_id)
    return loader.asset_config.get("symbol_universe", [])

def load_all_symbols_from_category(path: str = "config/symbol_category.yaml") -> List[str]:
    """Load all globally known asset symbols from category map."""
    print(f"📄 Loading global symbol list from: {path}")
    if not os.path.exists(path):
        print("⚠️ symbol_category.yaml not found — returning empty list")
        return []
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    print(f"✅ Loaded global symbol list — {len(data)} symbols")
    return list(data.keys())

class ConfigLoader:
    """
    ConfigLoader
    ============

    Handles the loading and saving of:
    - asset_config.yaml
    - portfolio_state.json
    - symbol universe and category map
    - historical net value snapshots
    """

    def __init__(self, client_id: str, base_dir: str = "clients"):
        self.client_id = client_id
        self.base_dir = base_dir
        self.client_dir = os.path.join(base_dir, client_id)

        print(f"🔧 Initializing ConfigLoader for client: {client_id}")
        print(f"📁 Client directory: {self.client_dir}")

        self.asset_config = self._load_asset_config()
        self.portfolio_state = self._load_portfolio_state()
        self.symbol_universe = self._load_symbol_universe()
        self.symbol_category_map = self._load_symbol_category_map()
        self.historical_net_value = self._load_net_value_history()

        print(f"✅ ConfigLoader ready for [{client_id}] — assets: {len(self.asset_config)}, symbols: {len(self.symbol_universe)}\n")

    def _load_asset_config(self) -> Dict:
        path = os.path.join(self.client_dir, "config", "asset_config.yaml")
        print(f"📄 Loading asset config from: {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"[{self.client_id}] asset_config.yaml not found: {path}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        print(f"✅ Loaded asset config — {len(data)} entries")
        return data

    def save_asset_config(self):
        """Save updated asset_config.yaml."""
        path = os.path.join(self.client_dir, "config", "asset_config.yaml")
        print(f"💾 Saving asset config to: {path}")
        with open(path, "w") as f:
            yaml.dump(self.asset_config, f, sort_keys=False)
        print("✅ asset_config.yaml saved")

    def get_risk_style(self) -> str:
        """Return the risk style defined in asset_config.yaml (default: 'conservative')"""
        return self.asset_config.get("risk_style", "conservative")

    def get_risk_constraints(self) -> Dict:
        """Return custom constraint dictionary from asset_config.yaml (if any)"""
        return self.asset_config.get("risk_constraints", {})

    def _load_portfolio_state(self) -> Dict:
        path = os.path.join(self.client_dir, "snapshots/current", "portfolio_state.json")
        print(f"📄 Loading portfolio state from: {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"[{self.client_id}] portfolio_state.json not found: {path}")
        with open(path, "r") as f:
            data = json.load(f)
        print(f"✅ Loaded portfolio state — keys: {list(data.keys())}")
        return data

    def save_portfolio_state(self):
        """Save updated portfolio state, with automatic backup."""
        path = os.path.join(self.client_dir, "snapshots/current", "portfolio_state.json")
        backup_path = os.path.join(self.client_dir, "snapshots/current", "portfolio_state_backup.json")

        print(f"💾 Saving portfolio state to: {path}")
        if os.path.exists(path):
            shutil.copy(path, backup_path)
            print(f"🗂️ Backup created at: {backup_path}")

        with open(path, "w") as f:
            json.dump(self.portfolio_state, f, indent=2)
        print("✅ Portfolio state saved\n")

    def _load_symbol_universe(self) -> List[str]:
        return load_all_symbols_from_category()

    def _load_symbol_category_map(self) -> Dict[str, str]:
        path = "config/symbol_category.yaml"
        print(f"📄 Loading symbol-category mapping from: {path}")
        if not os.path.exists(path):
            print("⚠️ symbol_category.yaml not found — returning empty map")
            return {}
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        print(f"✅ Loaded symbol-category map — {len(data)} entries")
        return {symbol: category for symbol, category in data.items()}

    def _load_net_value_history(self) -> List[float]:
        """
        Load structured net value history from JSONL via NetValueLogger.

        Returns:
            List[float]: sequence of daily net values (used for trend analysis, etc.)
        """
        logger = NetValueLogger(self.client_id, base_path=os.path.join(self.client_dir, "snapshots"))

        try:
            records = logger.load_all()
            net_values = [r["net_value"] for r in records if isinstance(r.get("net_value"), (int, float))]
            print(f"📈 Loaded {len(net_values)} historical net values")
            return net_values
        except Exception as e:
            print(f"❌ Failed to load net value history for {self.client_id}: {e}")
            return []
