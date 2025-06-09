# core/execution/execution_guard.py

class ExecutionGuard:
    """
    ExecutionGuard is responsible for validating trade intents
    before they proceed to execution.

    It enforces pre-execution rules to ensure:
    - Proper risk approval is attached
    - Trade was approved by the risk engine
    - Intent is well-formed and identifiable
    - (Optional) Duplicate prevention via audit hooks

    This acts as the final gatekeeper between the intent pipeline and the broker.
    """

    @staticmethod
    def validate_intent(intent):
        """
        Validate the integrity and approval status of a trade intent.

        Raises:
            PermissionError: If approval is missing or trade is rejected
            ValueError: If the intent ID is missing or malformed

        Returns:
            bool: True if the intent passes all checks
        """

        # 1. Ensure the intent has an attached approval object
        if not intent.approval:
            raise PermissionError("Intent has no approval attached. Trade denied.")

        # 2. Ensure the trade was approved by the risk engine
        if not intent.approval.get("approved", False):
            reason = intent.approval.get("reason", "No reason provided.")
            raise PermissionError(f"Trade intent rejected by risk system: {reason}")

        # 3. Validate presence and format of intent ID
        if not intent.intent_id or not isinstance(intent.intent_id, str):
            raise ValueError("Trade intent must have a valid unique intent_id.")

        # 4. (Optional) Check against audit log for duplicates
        # Example:
        # if audit_log.contains(intent.intent_id):
        #     raise PermissionError("Duplicate intent ID detected. Trade denied.")

        print(f"[ExecutionGuard] Intent validated: {intent.intent_id}")
        return True
