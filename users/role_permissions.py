# users/role_permissions.py

import yaml

# === 默认权限归属角色（用于提示/标注/校验） ===

PERMISSION_OWNERSHIP = {

    # === admin ===
    "admin.manage_users": "admin",  
    "admin.create_client": "admin",
    "admin.edit_asset_config": "admin",
    "admin.modify_role_permission": "admin",
    "admin.view_action_logs": "admin",
    "admin.trigger_global_killswitch": "admin",
    "admin.intraday_trigger_control": "admin",

    # === trader ===
    "trader.submit_manual_trade": "trader",
    "trader.view_portfolio": "trader",
    "trader.view_approval_status": "trader",

    # === risker ===
    "risker.approve_trade": "risker",
    "risker.view_intraday_trigger_log": "risker",
    "risker.view_risk_insight": "risker",
    "risker.trigger_global_killswitch": "risker",

        # === auditor ===
    "auditor.view_audit_decisions": "auditor",
    "auditor.view_daily_summary": "auditor",
    "auditor.trace_intent": "auditor",
    "auditor.view_periodic_scan_logs": "auditor",
    "auditor.view_risk_triggers": "auditor",


    # === compliance_officer ===
    "compliance_officer.view_logs": "compliance_officer",
    "compliance_officer.view_overrides": "compliance_officer",
    "compliance_officer.edit_rules": "compliance_officer",

    # === quant_researcher ===
    "quant_researcher.run_strategy": "quant_researcher",

    # === strategy_agent ===
    "strategy_agent.run_passive_rebalance": "strategy_agent",

    # === reporter ===
    "reporter.view_daily": "reporter",
    "reporter.view_monthly": "reporter",
    "reporter.view_attribution": "reporter",


}
