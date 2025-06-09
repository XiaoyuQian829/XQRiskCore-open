# broker/ibkr_adapter.py

from broker.broker_base import BrokerInterface

class IBKRAdapter(BrokerInterface):
    def __init__(self, config: dict):
        self.client_id = config.get("client_id")
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 7497)
        self.connected = False

        # TODO: Initialize IB API connection
        # from ib_insync import IB
        # self.ib = IB()
        # self.ib.connect(self.host, self.port, clientId=self.client_id)

    def get_price(self, symbol: str) -> float:
        raise NotImplementedError("IBKRAdapter.get_price is not implemented yet.")

    def place_order(self, symbol: str, quantity: int, action: str) -> dict:
        raise NotImplementedError("IBKRAdapter.place_order is not implemented yet.")

    def get_positions(self) -> dict:
        raise NotImplementedError("IBKRAdapter.get_positions is not implemented yet.")

    def get_account_info(self) -> dict:
        raise NotImplementedError("IBKRAdapter.get_account_info is not implemented yet.")
