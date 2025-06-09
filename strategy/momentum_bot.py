# strategy/momentum_bot.py

from strategy.strategy_base import StrategyModuleBase
from core.trade_intent import TradeIntent
from typing import List

class MomentumStrategy(StrategyModuleBase):
    def generate_trade_intents(self, symbol: str) -> List[TradeIntent]:
        df = self.ctx.market.get_price_history_100d(symbol)

        if df is None or df.empty or "close" not in df.columns:
            return []

        current_price = df["close"].iloc[-1]
        ma10 = df["close"].tail(10).mean()

        if current_price > ma10:
            return [
                TradeIntent(
                    symbol=symbol,
                    action="buy",
                    quantity=1,
                    notes="Momentum: price > 10-day MA",
                    trader_id="auto_momentum",
                    client_id=self.client_id,
                    source_type="strategy",
                    source="momentum",
                    strategy_id="momentum_v1"
                )
            ]

        return []

