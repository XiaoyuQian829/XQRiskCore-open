# core/execution/system_executor.py

from core.execution.base_executor import BaseExecutor
from core.execution.dry_run_executor import DryRunExecutor
from core.execution.live_executor import LiveOrderExecutor


class SystemExecutor(BaseExecutor):
    """
    Executor for system-triggered trades (e.g. risk rebalancing, auto-adjustments).

    Automatically routes to dry-run or live mode depending on client configuration.
    """

    def _run_execution(self, context):
        context.log("Executing system-triggered trade...")

        dry_run = context.client.config.get("dry_run", False)
        executor = DryRunExecutor() if dry_run else LiveOrderExecutor()

        # Delegate to selected executor (no local validation logic)
        executor._run_execution(context)
