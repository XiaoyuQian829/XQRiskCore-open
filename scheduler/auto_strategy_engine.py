# scheduler/auto_strategy_engine.py

from strategy.momentum_bot import MomentumBot
from users.load_user import load_user_instance

# === Load Strategy Role ===
# Load a simulated user instance with role "quantbot"
# This user has access to strategy module, market data, risk engine, and execution methods
role = load_user_instance("quantbot")
client = role.client  # Access the bound ClientContext

# === Initialize Strategy ===
# Create a MomentumBot instance for this client
strategy = MomentumBot(client_id=client.client_id)

# === Load Market Data ===
# Custom interface to load a unified DataFrame of tradable assets with historical price info
df = client.market.get_batch_price_df()

# === Run Strategy and Execute Intents ===
# Generate trade intents from strategy, submit for risk approval, and execute if approved
for intent in strategy.generate_trade_intents(df):
    approval = client.risk.approve_trade(intent)
    if approval["approved"]:
        client.execute(intent, approval)  # Optional: wrap with unified executor handler
