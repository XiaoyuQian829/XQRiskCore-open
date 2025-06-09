# `core/interfaces/` — Abstracted Service Interfaces

This module provides **standardized interfaces** to key services within the XQRiskCore system, enabling modular usage, external API exposure, and easier integration testing.

Each class isolates the logic of a major subsystem (e.g., strategy, risk, execution) and abstracts it into a clean callable interface.

---

## 📁 Available Interfaces

| Interface Class            | Purpose                                             | Underlying Module         |
|----------------------------|-----------------------------------------------------|----------------------------|
| `TradeFlowService`         | Unified trade lifecycle execution                   | `services/trade_flow.py`   |
| `RiskEvaluatorService`     | Evaluate trade intents with risk rules              | `risk_engine/controller.py`|
| `StrategySignalService`    | Generate trade signals via strategy module          | `strategy/momentum_strategy.py` |
| `MarketDataService`        | Fetch latest prices and historical market data      | `utils/market_data.py`     |

---

## 🧩 Usage Examples

### Submit a trade:

```python
from core.interfaces.trade_flow_service import TradeFlowService
svc = TradeFlowService(ctx)
result = svc.submit(intent)