# core/execution/shared_logic.py

from utils.time_utils import get_timestamps
from utils.trade_utils import simulate_slippage, estimate_commission

def simulate_trade_execution(context, slippage=0.001):
    intent = context.intent
    client = context.client

    price_info = client.market.get_price(intent.symbol)
    price = price_info["price"]
    timestamp = price_info.get("timestamp", get_timestamps()["now_ny"])
    context.log(f"Fetched market price: {price} @ {timestamp}")

    slippage_pct = 0.001
    exec_price = price + price * slippage_pct if intent.action == "buy" else price - price * slippage_pct
    context.log(f"Applied slippage: {round(slippage_pct * 100, 2)}% → Executed price: {exec_price:.4f}")

    commission = estimate_commission(intent.symbol, intent.quantity, exec_price, broker="generic")
    context.log(f"Estimated commission: ${commission:.4f}")

    client.portfolio.add_trade(
        symbol=intent.symbol,
        action=intent.action,
        quantity=intent.quantity,
        price=price,
        slippage_pct=slippage_pct
    )
    context.log(f"Portfolio updated with {intent.action} {intent.quantity} of {intent.symbol}.")

    client.trade_manager.add_trade(
        symbol=intent.symbol,
        action=intent.action,
        executed_price=exec_price,
        expected_price=price,
        slippage_pct=slippage_pct,
        execution_latency_ms=12,
        commission=commission,
        position_size=intent.quantity,
        source=intent.source,
        intent_id=intent.intent_id
    )
    context.log("Trade recorded by TradeManager.")

    client.live_updater.update()
    context.log("Live prices and net value updated.")

    client.drawdown_tracker.update()
    context.log("DrawdownTracker updated.")

    context.record_result(
        status="executed",
        reason="Approved",
        price=price,
        price_time=get_timestamps()["now_ny"].isoformat(),
        slippage_pct=slippage_pct,
        execution_latency_ms=12
    )
    client.logger.log_trade(context)
    context.log("Audit log written.")
    client.save()
    context.log("Portfolio state saved to disk.")