# demo/example_trade_submission.py

from core.interfaces.trade_flow_service import TradeFlowService
from utils.context_loader import get_client_context
from core.intent.trade_intent import TradeIntent

# Load context for trader "XiaoyuQ"
ctx = get_client_context("XiaoyuQ")

# Define trade intent
intent = TradeIntent(
    trader_id="XiaoyuQ",
    symbol="AAPL",
    action="BUY",
    quantity=1,
    notes="Demo intent"
)

# Use interface
svc = TradeFlowService(ctx)
result = svc.submit(intent)

print("Trade Status:", result.status)
print("Audit ID:", result.audit_id)
