# strategy/mean_reversion_bot.py

from strategy.strategy_base import StrategyModuleBase
from core.trade_intent import TradeIntent
from typing import List

class MeanReversionBot(StrategyModuleBase):
    def generate_trade_intents(self, symbol: str) -> List[TradeIntent]:
        df = self.ctx.market.get_price_history_100d(symbol)

        if df is None or df.empty or "close" not in df.columns:
            return []

        df["ma"] = df["close"].rolling(20).mean()
        df["std"] = df["close"].rolling(20).std()
        df["lower_band"] = df["ma"] - 2 * df["std"]

        latest = df.iloc[-1]
        if latest["close"] < latest["lower_band"]:
            return [
                TradeIntent(
                    symbol=symbol,
                    action="buy",
                    quantity=1,
                    notes="Mean Reversion: price < MA - 2σ",
                    trader_id="auto_meanrev",
                    client_id=self.client_id,
                    source_type="strategy",
                    source="mean_reversion",
                    strategy_id="meanrev_v1"
                )
            ]

        return []
