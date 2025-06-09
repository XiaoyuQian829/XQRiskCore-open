# audit/action_logger.py

import os
import json
from datetime import datetime
from typing import Optional

from core.request_context import RequestContext


class ActionLogger:
    """
    ActionLogger
    ============

    Centralized behavioral logger for all user and system activity in XQRiskCore.

    Supported event types:
    ----------------------
    - "view":      Passive user events, such as opening pages, charts, or logs
    - "action":    Active user submissions, such as placing trades or saving configurations
    - "system":    Automated system behaviors (e.g., background scans, strategy executions)

    Logging Design:
    ---------------
    - Each event is logged in structured JSONL format (1 JSON per line)
    - Logs are stored by role → user → date, enabling traceability and filtering
    - Supports real-time debug printing and structured audit trail storage

    Example log path:
    -----------------
    audit/user_action_logs/admin/alice/2025-06-09/events.jsonl
    """

    def __init__(self, user_id: str, role: str, module: str):
        """
        Initialize the logger for a specific user, role, and logical module.
        Creates a folder structure like:
            audit/user_action_logs/<role>/<user_id>/<YYYY-MM-DD>/
        """
        self.user_id = user_id
        self.role = role
        self.module = module

        # Get current date (used for folder-level log partitioning)
        today = datetime.now().strftime("%Y-%m-%d")

        # Construct log directory path
        log_dir = os.path.join("audit", "user_action_logs", role, user_id, today)

        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Final log file path (JSONL format)
        self.log_path = os.path.join(log_dir, "events.jsonl")

    def log(
        self,
        ctx: RequestContext,
        action: str,
        payload: Optional[dict] = None,
        status: str = "ok",
        event_type: str = "action"
    ):
        """
        Log a structured behavioral event.

        Args:
            ctx (RequestContext): Current request/session context
            action (str): Name of the action performed (e.g. "submit_trade", "save_config")
            payload (dict): Optional metadata attached to the action
            status (str): Result status ("ok", "error", "denied")
            event_type (str): One of {"view", "action", "system"}
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,         # Type of behavior (used for filtering/grouping)
            "user": ctx.user_id,              # Acting user ID
            "role": ctx.role,                 # User role (e.g. admin, auditor, trader)
            "client": ctx.client_id,          # Which client portfolio this action applied to
            "source": ctx.source,             # Where the action originated (e.g. "login", "api", "dashboard")
            "module": self.module,            # Logical module where this action was triggered
            "action": action,                 # High-level label of the action
            "status": status,                 # Outcome status
            "payload": payload or {},         # Any structured metadata for future reference
            "module_version": getattr(ctx, "system_version", "v1.0.0")  # Optional version tag
        }

        # Attempt to write to file
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"❌ Failed to log action: {e}")

        # Optional real-time printing (can be turned off via env)
        if os.getenv("ACTION_LOG_VERBOSE", "1") == "1":
            print(f"📝 [{event_type.upper()}] {action} | user={ctx.user_id} | client={ctx.client_id}")


# === Unified Logging Helpers ===

def record_user_action(ctx: RequestContext, module: str, action: str, payload: Optional[dict] = None):
    """
    Record an interactive user action (e.g., submit trade, press button).

    Args:
        ctx (RequestContext): Current session context
        module (str): Subsystem where the action occurred
        action (str): Label of the action (e.g., "submit_trade")
        payload (dict): Optional metadata for audit review
    """
    logger = ActionLogger(ctx.user_id, ctx.role, module)
    logger.log(ctx, action=action, payload=payload, event_type="action")


def record_user_view(ctx: RequestContext, module: str, action: str = "view", payload: Optional[dict] = None):
    """
    Record a passive user viewing event (e.g., opening a chart, switching tab).

    Args:
        ctx (RequestContext): Current session context
        module (str): Subsystem viewed
        action (str): Optional view action label (defaults to "view")
        payload (dict): Optional metadata (e.g., asset symbol, section name)
    """
    logger = ActionLogger(ctx.user_id, ctx.role, module)
    logger.log(ctx, action=action, payload=payload, event_type="view")


def record_system_event(module: str, action: str, payload: Optional[dict] = None, status: str = "ok"):
    """
    Record a system-generated behavior (e.g., scheduled scan, auto rebalance).

    This does not rely on a user session.

    Args:
        module (str): Subsystem that triggered the event
        action (str): Label of system event
        payload (dict): Optional event metadata
        status (str): Event outcome status
    """
    # Create a synthetic session context to represent the system
    dummy_ctx = RequestContext(user_id="system", role="system", client_id="global", source="engine")

    logger = ActionLogger(user_id="system", role="system", module=module)
    logger.log(dummy_ctx, action=action, payload=payload, status=status, event_type="system")
