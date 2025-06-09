# core/emergency/trade_audit_failsafe.py

from core.client_context import ClientContext

class TradeAuditFailSafe:
    """
    TradeAuditFailSafe
    ------------------
    Ensures that audit logs are successfully recorded.
    If audit record is missing or invalid, block trade.
    """

    def __init__(self, ctx: ClientContext):
        self.ctx = ctx

    def check(self) -> tuple[bool, str]:
        """
        Checks whether the audit record was properly written.
        Returns (allowed: bool, reason: str)
        """
        record = getattr(self.ctx, "latest_audit_record", None)

        if not record:
            return False, "❌ No audit record found. Trade blocked by TradeAuditFailSafe."

        if isinstance(record, dict) and record.get("status") == "ok":
            return True, "✅ Audit log verified."

        return False, "❌ Audit log invalid or incomplete. Trade blocked by TradeAuditFailSafe."