# utils/executor_router.py

from core.execution.manual_executor import ManualExecutor
from core.execution.strategy_executor import StrategyExecutor
from core.execution.system_executor import SystemExecutor

def get_executor(intent):
    if intent.source_type == "manual":
        return ManualExecutor()
    elif intent.source_type == "strategy":
        return StrategyExecutor()
    else:
        return SystemExecutor()
