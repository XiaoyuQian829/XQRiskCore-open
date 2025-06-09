# backtest/backtest_client_context.py

class BacktestClientContext:
    """
    BacktestClientContext (under development)
    ==========================================
    Placeholder class for simulating ClientContext in backtesting mode.

    Intended use:
    - Simulate portfolio state evolution over time
    - Apply passive and strategy-driven trades to historical data
    - Evaluate risk engine decisions in retrospective

    Planned Features:
    - Historical price fetching & time-travel simulation
    - Context-aware trade lifecycle execution
    - Risk rule application and audit trail during backtest
    - Output daily snapshots and cumulative performance

    Status: ⚠️ Not yet implemented
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.mock_state = {}
        self.history_cursor = None
        self.current_date = None
        self.market_data_provider = None  # placeholder
        self.simulated_portfolio = {}  # placeholder for positions
        self.logs = []

    def load_mock_config(self):
        # TODO: Load asset_config and initial state
        pass

    def run_backtest(self):
        # TODO: Core loop for daily simulation
        raise NotImplementedError("Backtest execution loop not yet implemented.")

    def apply_trade_intent(self, intent):
        # TODO: Simulate trade intent execution
        raise NotImplementedError("Trade intent simulation not yet supported.")

    def snapshot(self):
        # TODO: Return current simulated state
        return {
            "date": self.current_date,
            "portfolio": self.simulated_portfolio,
            "logs": self.logs,
        }
