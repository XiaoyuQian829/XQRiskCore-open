# audit/audit_logger.py

import os
import json
from utils.time_utils import get_timestamps
from utils.trade_utils import simulate_slippage


class AuditLogger:
    """
    AuditLogger — Centralized Compliance Event Recorder
    ===================================================

    This class handles all persistent audit logs for a given client.
    It supports structured JSONL outputs across multiple categories,
    ensuring a full record of trade decisions, risk triggers, and strategy behavior.

    Log Types (Directory Layout):
    -----------------------------
    clients/<client_id>/audit/
    ├── decisions/             ← Trade approval and execution history
    ├── cooling_off_logs/      ← Silent mode triggers/releases (per symbol or account)
    ├── killswitch_logs/       ← Emergency kill switch activations/releases
    ├── daily_summary/         ← Daily account-wide metrics and events
    ├── monthly_optimizer/     ← Strategy feedback, performance, and suggestions
    └── periodic_scan_logs/    ← Outputs from scheduled or intraday risk scans
    """

    def __init__(self, client_id: str):
        """
        Initialize the audit logger for a specific client.

        Creates directory structure if missing.
        """
        self.client_id = client_id
        self.root_dir = os.path.join("clients", client_id, "audit")
        self.ensure_dirs([
            "decisions",
            "cooling_off_logs",
            "killswitch_logs",
            "daily_summary",
            "monthly_optimizer",
            "periodic_scan_logs"
        ])

    def ensure_dirs(self, subfolders):
        """
        Create subdirectories under the audit root directory, if they don't exist.
        Ensures proper separation of audit types.
        """
        for folder in subfolders:
            os.makedirs(os.path.join(self.root_dir, folder), exist_ok=True)

    def _write_jsonl(self, subfolder: str, record: dict):
        """
        Append a dictionary record to a date-based JSONL file.

        Args:
            subfolder (str): One of the predefined audit categories.
            record (dict): Structured event object to write.
        """
        today = get_timestamps()["date_str"]
        path = os.path.join(self.root_dir, subfolder, f"{today}.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            json.dump(record, f)
            f.write("\n")

    def log_trade(self, context):
        """
        Record the full trade lifecycle, including:
        - intent metadata
        - risk approval signals
        - execution result (price, status, latency)
        - system state (broker, dry_run, triggered risk flags)
        """
        result = context.result
        intent = context.intent
        approval = intent.approval or {}
        snapshot = context.client.portfolio.to_snapshot()

        record = {
            "intent": {
                "intent_id": intent.intent_id,
                "timestamp": result.get("timestamp"),
                "client_id": context.client.client_id,
                "trader_id": intent.trader_id,
                "strategy_id": intent.strategy_id,
                "symbol": intent.symbol,
                "action": intent.action,
                "quantity": intent.quantity,
                "source_type": intent.source_type,
                "source": intent.source,
                "notes": intent.metadata.get("notes")
            },
            "approval": {
                "time": result.get("timestamp"),
                "approved": approval.get("approved"),
                "risk_style": context.client.risk_style,
                "reason": result.get("reason"),
                "reason_code": result.get("reason_code"),
                "score": result.get("score"),
                "signals": result.get("signals", {})
            },
            "execution": {
                "status": result.get("status"),
                "status_code": result.get("status_code"),
                "price": result.get("price"),
                "expected_price": result.get("expected_price"),
                "price_time": result.get("price_time"),
                "slippage_pct": result.get("slippage_pct") or simulate_slippage(
                    executed_price=result.get("price") or 0.0,
                    expected_price=result.get("expected_price") or result.get("price") or 1.0
                ),
                "execution_latency_ms": result.get("execution_latency_ms"),
                "commission": result.get("commission", 0.0)
            },
            "execution_context": {
                "dry_run": result.get("dry_run"),
                "broker": result.get("broker")
            },
            "executor_type": context.executor_type,
            "portfolio_snapshot": snapshot,
            "risk_event_flags": {
                "cooling_off_triggered": getattr(context, "cooling_off_triggered", False),
                "killswitch_triggered": getattr(context, "killswitch_triggered", False)
            },
            "system_version": getattr(context, "system_version", "v1.0.0"),
            "intraday_snapshot": getattr(context, "intraday_snapshot", None)
        }

        context.audit_record = record
        self._write_jsonl("decisions", record)
        return record

    def log_silent_mode(self, level: str, symbol: str = None, reason: str = None,
                        user_id: str = None, strategy_id: str = None,
                        trigger_type: str = "manual", trigger_source: str = "admin_panel",
                        reason_code: str = "MANUAL_ADMIN_TRIGGER", expected_release: str = None,
                        intent_id: str = None):
        """
        Record activation of silent mode (cooling off).
        Supports both symbol-level and account-level freezing.
        """
        self._write_jsonl("cooling_off_logs", {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "event": "silent_mode_triggered",
            "level": level,                         # "symbol" or "account"
            "symbol": symbol,
            "trigger_type": trigger_type,           # "manual" or "system"
            "trigger_source": trigger_source,       # e.g., "admin_panel", "intraday_engine"
            "reason_code": reason_code,
            "reason_text": reason,
            "user_id": user_id,
            "strategy_id": strategy_id,
            "expected_release": expected_release,
            "intent_id": intent_id
        })

    def log_release_silent(self, level: str, symbol: str = None, user_id: str = None,
                           release_type: str = "manual", released_by: str = None,
                           reason_code: str = "MANUAL_RELEASE", duration_sec: int = None):
        """
        Record a manual or automatic release of silent mode lock.
        """
        self._write_jsonl("cooling_off_logs", {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "event": "silent_mode_released",
            "level": level,
            "symbol": symbol,
            "release_type": release_type,
            "released_by": released_by or user_id,
            "reason_code": reason_code,
            "duration_sec": duration_sec
        })

    def log_killswitch(self, level: str, reason: str, user_id: str = None,
                       trigger_source: str = "drawdown_monitor", reason_code: str = "TRAILING_MDD"):
        """
        Record a kill switch trigger (account-level block).
        Usually caused by severe risk breach.
        """
        self._write_jsonl("killswitch_logs", {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "event": "killswitch_triggered",
            "level": level,                        # "account" or "system"
            "reason": reason,
            "reason_code": reason_code,
            "user_id": user_id,
            "trigger_source": trigger_source
        })

    def log_release_killswitch(self, level: str, symbol: str = None, user_id: str = None,
                                release_type: str = "manual", released_by: str = None,
                                reason_code: str = "MANUAL_RELEASE"):
        """
        Record a release event of the kill switch lock.
        Includes manual release audit trail.
        """
        self._write_jsonl("killswitch_logs", {
            "timestamp": get_timestamps()["now_ny"].isoformat(),
            "event": "killswitch_released",
            "level": level,
            "symbol": symbol,
            "user_id": user_id,
            "release_type": release_type,
            "released_by": released_by or user_id,
            "reason_code": reason_code
        })

    def log_daily_summary(self, summary_dict: dict):
        """
        Append a daily snapshot of portfolio state and triggered events.
        Used for reporting, feedback, and retrospective optimization.
        """
        summary_dict["timestamp"] = get_timestamps()["now_ny"].isoformat()
        summary_dict["scan_type"] = "daily_summary"
        self._write_jsonl("daily_summary", summary_dict)

    def log_monthly_optimizer(self, result_dict: dict):
        """
        Record monthly optimization results or strategic feedback.
        Used for model tuning, performance tracking, and rebalancing recommendations.
        """
        result_dict["timestamp"] = get_timestamps()["now_ny"].isoformat()
        result_dict["scan_type"] = "monthly_optimizer"
        self._write_jsonl("monthly_optimizer", result_dict)

    def log_periodic_scan(self, scan_dict: dict, trigger_interval_min: int = None):
        """
        Log the result of scheduled or real-time portfolio scans.
        Useful for understanding intraday drawdown triggers or volatility spikes.
        """
        scan_dict["timestamp"] = get_timestamps()["now_ny"].isoformat()
        if trigger_interval_min is not None:
            scan_dict["scan_type"] = f"{trigger_interval_min}min_intraday_scan"
        else:
            scan_dict["scan_type"] = "unspecified_interval_scan"
        self._write_jsonl("periodic_scan_logs", scan_dict)


