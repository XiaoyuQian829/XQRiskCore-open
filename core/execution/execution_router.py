# core/execution/execution_router.py

from core.execution.manual_executor import ManualExecutor
from core.execution.strategy_executor import StrategyExecutor
from core.execution.system_executor import SystemExecutor
from core.execution.dry_run_executor import DryRunExecutor
from core.execution.live_executor import LiveOrderExecutor


def get_executor_by_source(source_type: str, dry_run: bool):
    """
    Return the appropriate executor instance based on source type.

    Args:
        source_type (str): The origin of the trade intent — "manual", "strategy", or "system"
        dry_run (bool): Whether to simulate the execution (no real order placed)

    Returns:
        Executor instance (BaseExecutor subclass)
    """
    if source_type == "manual":
        return ManualExecutor()
    elif source_type == "strategy":
        return StrategyExecutor()
    elif source_type == "system":
        return SystemExecutor()
    else:
        return StrategyExecutor()  # Fallback to strategy executor for unknown types


def get_execution_path_for_direct_use(dry_run: bool):
    """
    Return a generic execution path without source context.
    Used when execution is called from a simple pipeline or backend test.

    Args:
        dry_run (bool): Whether to run in simulation mode

    Returns:
        DryRunExecutor or LiveOrderExecutor
    """
    return DryRunExecutor() if dry_run else LiveOrderExecutor()


def get_executor_for_client(client_ctx):
    """
    Route execution based on the client's dry_run setting.

    Args:
        client_ctx: The ClientContext instance for the trade

    Returns:
        DryRunExecutor or LiveOrderExecutor
    """
    return DryRunExecutor() if client_ctx.dry_run else LiveOrderExecutor()
