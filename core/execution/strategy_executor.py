# core/execution/strategy_executor.py

from core.execution.base_executor import BaseExecutor
from core.execution.dry_run_executor import DryRunExecutor
from core.execution.live_executor import LiveOrderExecutor


class StrategyExecutor(BaseExecutor):
    """
    Executor for strategy-generated trade intents.

    Delegates to dry-run or live execution depending on client config.
    """

    def _run_execution(self, context):
        context.log("Executing strategy trade...")

        dry_run = context.client.config.get("dry_run", False)
        executor = DryRunExecutor() if dry_run else LiveOrderExecutor()

        # Delegate execution without applying additional logic here
        executor._run_execution(context)
