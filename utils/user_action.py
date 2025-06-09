# utils/user_action.py

class UserAction:

    # 👨‍💼 Admin
    VIEW_USER_MANAGER            = "view_user_manager"           # roles/admin/pages/user_manager.py
    VIEW_CLIENT_MANAGER          = "view_client_manager"         # roles/admin/pages/client_manager.py
    VIEW_ASSET_MANAGER           = "view_asset_manager"          # roles/admin/pages/asset_manager.py
    VIEW_ACTION_LOG              = "view_action_log"             # roles/admin/pages/action_log_viewer.py
    VIEW_PERMISSION_EDITOR       = "view_permission_editor"      # roles/admin/pages/permission_editor.py
    VIEW_RUNTIME_CONTROLS        = "view_runtime_controls"       # roles/admin/pages/runtime_controls.py
    VIEW_INTRADAY_TRIGGER_SETTINGS = "view_intraday_trigger_settings"  # roles/admin/pages/intraday_trigger_control.py
    SAVE_TRIGGER_SETTINGS        = "save_trigger_settings"

    # 👤 Trader
    VIEW_PORTFOLIO               = "view_portfolio"              # roles/trader/pages/portfolio_view.py
    VIEW_TRADE_FORM              = "view_trade_form"             # roles/trader/pages/trade_form.py
    SUBMIT_FORM                  = "submit_form"                 # ⬅️ on submit button in trade_form
    VIEW_APPROVAL_STATUS         = "view_approval_status"        # roles/trader/pages/approval_status_viewer.py


    # 🧠 Risker
    VIEW_INTRADAY_TRIGGER_LOGS   = "view_intraday_trigger_logs"  # roles/risker/pages/intraday_trigger_log_viewer.py
    VIEW_RISK_INSIGHT            = "view_risk_insight"           # roles/risker/pages/risk_insight.py
    VIEW_APPROVAL_PANEL          = "view_approval_panel"         # roles/risker/pages/approval_panel.py
    VIEW_RUNTIME_CONTROLS        = "view_runtime_controls"  # roles/risker/pages/runtime_controls.py

    # 📊 Auditor
    VIEW_AUDIT_DECISIONS         = "view_audit_decisions"        # roles/auditor/pages/audit_decisions_viewer.py
    VIEW_INTENT_TRACER           = "view_intent_tracer"          # roles/auditor/pages/intent_tracer.py
    VIEW_PERIODIC_SCAN_LOGS      = "view_periodic_scan_logs"     # roles/auditor/pages/periodic_scan_logs_viewer.py
    VIEW_RISK_TRIGGERS           = "view_risk_triggers"          # roles/auditor/pages/risk_triggers_viewer.py
    VIEW_DAILY_SUMMARY           = "view_daily_summary"          # roles/auditor/pages/daily_summary_viewer.py
    DOWNLOAD_PDF                 = "download_pdf"
    DOWNLOAD_CSV                 = "download_csv"

    # ⚙️ Strategy Agent
    VIEW_PASSIVE_REBALANCER      = "view_passive_rebalancer"     # roles/strategy_agent/pages/passive_rebalancer.py
#    SUBMIT_FORM                  = "submit_form"                

    # 🧪 Quant Researcher
    VIEW_STRATEGY_RUNNER         = "view_strategy_runner"        # roles/quant_researcher/pages/strategy_runner.py
#    SUBMIT_STRATEGY_CONFIG       = "submit_strategy_config"      

    # Compliance_officer
    VIEW_RULE_EDITOR = "view_rule_editor"
    VIEW_COMPLIANCE_LOGS = "view_compliance_logs"
    VIEW_MANUAL_OVERRIDES = "view_manual_overrides"

    # Reporter
    VIEW_DAILY_REPORT = "view_daily_report"
    VIEW_MONTHLY_SUMMARY = "view_monthly_summary"
    VIEW_ATTRIBUTION_BREAKDOWN = "view_attribution_breakdown"


    LOGIN                        = "login"
    LOGOUT                       = "logout"
    RESET_SESSION                = "reset_session"
    REFRESH_TRIGGERED            = "refresh_page"

    SWITCH_PAGE                  = "switch_page"
    VIEW_MODULE                  = "view_module"
    CUSTOM_EVENT                 = "custom_event"
