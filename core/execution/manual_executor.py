# core/execution/manual_executor.py

from core.execution.base_executor import BaseExecutor
from core.execution.dry_run_executor import DryRunExecutor
from core.execution.live_executor import LiveOrderExecutor


class ManualExecutor(BaseExecutor):
    """
    Executor for manually submitted trades.

    Delegates to dry-run or live execution based on client config.
    """

    def _run_execution(self, context):
        context.log("Executing manual trade...")

        dry_run = context.client.config.get("dry_run", False)
        executor = DryRunExecutor() if dry_run else LiveOrderExecutor()

        # Directly invoke underlying executor (no additional guards here)
        executor._run_execution(context)
