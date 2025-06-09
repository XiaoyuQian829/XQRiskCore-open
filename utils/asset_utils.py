# utils/asset_utils.py

import yaml
import os
from functools import lru_cache

def _default_category_map():
    """
    Default asset category mapping.

    Used as fallback if config file is missing.
    """
    return {
        "SPY": "ETFs", "QQQ": "ETFs", "VTI": "ETFs", "XLK": "ETFs",
        "XLF": "ETFs", "XLE": "ETFs", "XLV": "ETFs", "XLU": "ETFs",
        "BND": "Bonds", "TLT": "Bonds", "IEF": "Bonds", "AGG": "Bonds"
    }

@lru_cache(maxsize=1)
def load_symbol_category(path: str = "config/symbol_category.yaml") -> dict:
    """
    Load symbol-to-category mapping from YAML config file.

    If file not found or fails to load, fallback to built-in default map.
    Uses LRU cache to avoid repeated file reads.

    Args:
        path (str): Path to YAML file with symbol → category mapping.

    Returns:
        dict: Mapping of asset symbols to categories (e.g., "Stocks", "ETFs", "Bonds")
    """
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[Warning] Failed to load symbol_category.yaml, using default: {e}")
    return _default_category_map()

def get_asset_category(symbol: str) -> str:
    """
    Get the category of a given asset symbol.

    If the symbol is not explicitly defined, default to "Stocks".

    Args:
        symbol (str): Asset symbol (e.g., "AAPL", "SPY")

    Returns:
        str: Category name ("Stocks", "ETFs", "Bonds", etc.)
    """
    category_map = load_symbol_category()
    return category_map.get(symbol, "Stocks")

def get_asset_rebalance_schedule(symbol: str) -> dict:
    """
    Determine the rebalance frequency for a given asset symbol.

    Logic:
    - ETFs: Monthly rebalance
    - Bonds: Quarterly rebalance
    - Stocks (default): Weekly rebalance

    Args:
        symbol (str): Asset symbol

    Returns:
        dict: Schedule definition, e.g., {"rebalance": "monthly"}
    """
    asset_type = get_asset_category(symbol)
    if asset_type == "ETFs":
        return {"rebalance": "monthly"}
    elif asset_type == "Bonds":
        return {"rebalance": "quarterly"}
    else:
        return {"rebalance": "weekly"}
