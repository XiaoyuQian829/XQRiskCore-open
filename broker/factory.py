# broker/factory.py

from broker.alpaca_adapter import AlpacaAdapter
from broker.ibkr_adapter import IBKRAdapter
from broker.tiger_adapter import TigerAdapter
from typing import Dict
from broker.broker_base import BrokerInterface


def get_broker(config: Dict) -> BrokerInterface:
    """
    Load the appropriate broker adapter based on client config.
    Expected config structure:
        - broker: e.g., "alpaca", "ibkr", "tiger"
        - broker_keys: dict containing API keys or credentials
    """
    broker_name = config.get("broker", "").lower()
    keys = config.get("broker_keys", {})

    if broker_name == "alpaca":
        return AlpacaAdapter(keys)
    elif broker_name == "ibkr":
        return IBKRAdapter(keys)
    elif broker_name == "tiger":
        return TigerAdapter(keys)
    else:
        raise ValueError(f"Unsupported broker: '{broker_name}'")
