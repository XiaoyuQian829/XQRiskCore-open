# frontend/page_registry/role_page_map.py

"""
Role-to-Page Registry
=====================
This module defines the mapping between user roles and their accessible frontend pages.

Each entry:
- Key = role name (e.g., "admin", "trader", "auditor")
- Value = dict of {label → (permission_key, page_render_module)}

If permission_key is None, the page is a welcome panel and is always shown for that role.
"""

# --- Import all page modules grouped by role ---

from frontend.roles.admin.pages import (
    admin_home, user_manager, client_manager, asset_manager, permission_editor,
    action_log_viewer, admin_runtime_controls, intraday_trigger_control
)
from frontend.roles.trader.pages import (
    trader_home, approval_status_viewer, portfolio_view, trade_form
)
from frontend.roles.risker.pages import (
    risker_home, approval_panel, risk_insight, risker_runtime_controls, intraday_trigger_log_viewer
)
from frontend.roles.auditor.pages import (
    auditor_home, audit_decisions_viewer, risk_triggers_viewer, daily_summary_viewer,
    periodic_scan_logs_viewer, intent_tracer
)
from frontend.roles.compliance_officer.pages import (
    rule_editor, compliance_log_viewer, manual_override_log
)
from frontend.roles.quant_researcher.pages import strategy_runner
from frontend.roles.strategy_agent.pages import passive_rebalancer
from frontend.roles.reporter.pages import (
    daily_report_viewer, monthly_summary, attribution_breakdown
)

# === Master registry: role → {label → (permission_key, module)} ===

ROLE_PAGE_REGISTRY = {
    "admin": {
        "Admin: Welcome Panel 🟦": (None, admin_home),
        "Admin: User & Role Manager": ("admin.manage_users", user_manager),
        "Admin: Client Registry Config": ("admin.create_client", client_manager),
        "Admin: Tradable Asset Config": ("admin.edit_asset_config", asset_manager),
        "Admin: Role Permission Matrix": ("admin.modify_role_permission", permission_editor),
        "Admin: Intraday Trigger Rules": ("admin.intraday_trigger_control", intraday_trigger_control),
        "Admin: Runtime Control Panel": ("admin.trigger_global_killswitch", admin_runtime_controls),
        "Admin: User Action Logs": ("admin.view_action_logs", action_log_viewer),
    },
    "trader": {
        "Trader: Welcome Panel 🟩": (None, trader_home),
        "Trader: Portfolio Overview": ("trader.view_portfolio", portfolio_view),
        "Trader: Manual Trade Submit": ("trader.submit_manual_trade", trade_form),
        "Trader: Approval Status Tracker": ("trader.view_approval_status", approval_status_viewer),
    },
    "risker": {
        "Risker: Welcome Panel 🟧": (None, risker_home),
        "Risker: Trade Approval Panel": ("risker.approve_trade", approval_panel),
        "Risker: Risk Signal Dashboard": ("risker.view_risk_insight", risk_insight),
        "Risker: Runtime Safeguards": ("risker.trigger_global_killswitch", risker_runtime_controls),
        "Risker: Trigger Scan History": ("risker.view_intraday_trigger_log", intraday_trigger_log_viewer),
    },
    "auditor": {
        "Audit: Welcome Panel 🟪": (None, auditor_home),
        "Audit: Intent Trace Viewer": ("auditor.trace_intent", intent_tracer),
        "Audit: Decision Records": ("auditor.view_audit_decisions", audit_decisions_viewer),
        "Audit: Trigger Event Logs": ("auditor.view_risk_triggers", risk_triggers_viewer),
        "Audit: Daily Oversight Sheet": ("auditor.view_daily_summary", daily_summary_viewer),
        "Audit: Periodic Scan Logs": ("auditor.view_periodic_scan_logs", periodic_scan_logs_viewer),
    },
    "compliance_officer": {
        "Compliance: Rule Editor": ("compliance_officer.edit_rules", rule_editor),
        "Compliance: Log Review Panel": ("compliance_officer.view_logs", compliance_log_viewer),
        "Compliance: Override Tracker": ("compliance_officer.view_overrides", manual_override_log),
    },
    "quant_researcher": {
        "Quant: Strategy Runner": ("quant_researcher.run_strategy", strategy_runner),
    },
    "strategy_agent": {
        "Strategy: Passive Rebalancer": ("strategy_agent.run_passive_rebalance", passive_rebalancer),
    },
    "reporter": {
        "Report: Daily Performance Report": ("reporter.view_daily", daily_report_viewer),
        "Report: Monthly Summary View": ("reporter.view_monthly", monthly_summary),
        "Report: Attribution Breakdown": ("reporter.view_attribution", attribution_breakdown),
    },
}




# === Utility: Filter visible pages based on role permissions ===

def get_visible_pages(ctx):
    """
    Return a filtered list of pages visible to the current user.

    Logic:
    - Pages with `None` permission are always visible if role matches
    - Other pages are shown only if the user has the required permission
    """
    from core.permissions_manager import PermissionsManager
    pm = PermissionsManager()
    pm.reload()
    user_perms = pm.get_role_permissions(ctx.role)

    visible = {}
    for role, pages in ROLE_PAGE_REGISTRY.items():
        for label, (perm, module) in pages.items():
            if perm is None:
                if role == ctx.role:
                    visible[label] = (perm, module)
            elif user_perms.get(perm, False):
                visible[label] = (perm, module)

    return visible


# === Utility: Export role → [visible page labels] ===

def export_role_permission_matrix():
    """
    Export a permission matrix showing which pages are visible to each role.

    Returns:
        dict: role → list of visible page labels
    """
    pm = PermissionsManager()
    roles = pm.get_all_roles()

    matrix = {}
    for role in roles:
        perms = pm.get_role_permissions(role)
        role_pages = ROLE_PAGE_REGISTRY.get(role, {})
        visible = [
            label for label, (perm, _) in role_pages.items()
            if perm is None or perms.get(perm, False)
        ]
        matrix[role] = visible

    return matrix




