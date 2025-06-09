# broker/tiger_adapter.py

from broker.broker_base import BrokerInterface

class TigerAdapter(BrokerInterface):
    def __init__(self, config: dict):
        self.account = config.get("account")
        self.token = config.get("token")
        self.env = config.get("env", "paper")  # options: paper or live

        # TODO: Initialize Tiger OpenAPI SDK
        # Example:
        # from tigeropen.tiger_open_client import TigerOpenClient
        # self.client = TigerOpenClient(...)
        # self.client.connect()

    def get_price(self, symbol: str) -> float:
        raise NotImplementedError("TigerAdapter.get_price is not implemented yet.")

    def place_order(self, symbol: str, quantity: int, action: str) -> dict:
        raise NotImplementedError("TigerAdapter.place_order is not implemented yet.")

    def get_positions(self) -> dict:
        raise NotImplementedError("TigerAdapter.get_positions is not implemented yet.")

    def get_account_info(self) -> dict:
        raise NotImplementedError("TigerAdapter.get_account_info is not implemented yet.")
