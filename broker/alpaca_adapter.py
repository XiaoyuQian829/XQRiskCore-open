# broker/alpaca_adapter.py

import os
from alpaca_trade_api import REST
from broker.broker_base import BrokerInterface  # make sure this import is correct

class AlpacaAdapter(BrokerInterface):
    def __init__(self, config: dict):
        # Use provided keys or fallback to environment variables
        self.key = config.get("key") or os.getenv("APCA_API_KEY_ID")
        self.secret = config.get("secret") or os.getenv("APCA_API_SECRET_KEY")
        self.endpoint = "https://paper-api.alpaca.markets"

        if not self.key or not self.secret:
            raise ValueError("Missing Alpaca API key or secret.")

        self.api = REST(self.key, self.secret, base_url=self.endpoint)

    def get_price(self, symbol: str) -> float:
        quote = self.api.get_latest_trade(symbol)
        return quote.price

    def place_order(self, symbol: str, quantity: int, action: str) -> dict:
        side = "buy" if action.lower() == "buy" else "sell"
        order = self.api.submit_order(
            symbol=symbol,
            qty=quantity,
            side=side,
            type="market",
            time_in_force="day"
        )
        return {
            "id": order.id,
            "symbol": order.symbol,
            "qty": order.qty,
            "status": order.status,
            "submitted_at": order.submitted_at.isoformat()
        }

    def get_positions(self) -> dict:
        positions = self.api.list_positions()
        return {pos.symbol: {
                    "qty": float(pos.qty),
                    "avg_price": float(pos.avg_entry_price),
                    "market_value": float(pos.market_value)
                } for pos in positions}

    def get_account_info(self) -> dict:
        acct = self.api.get_account()
        return {
            "equity": float(acct.equity),
            "cash": float(acct.cash),
            "buying_power": float(acct.buying_power),
            "portfolio_value": float(acct.portfolio_value)
        }
