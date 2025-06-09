# core/execution/base_executor.py

from core.execution.execution_guard import ExecutionGuard

class BaseExecutor:
    def __init__(self):
        pass

    def execute(self, context):
        context.executor_type = self.__class__.__name__ 
        self._guard(context)
        self._run_execution(context)

    def _guard(self, context):
        ExecutionGuard.validate_intent(context.intent)

    def _run_execution(self, context):
        raise NotImplementedError("Subclasses must implement _run_execution()")
