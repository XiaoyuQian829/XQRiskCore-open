# risk_engine/signals/risk_signals.py

from utils.time_utils import get_timestamps

class RiskSignalSet:
    """
    RiskSignalSet
    =============
    A standardized container for daily risk scoring used throughout the system.
    Encapsulates regime classification, volatility, VaR, CVaR, and composite risk score.

    It supports:
    - Score computation from raw inputs (regime, volatility, etc.)
    - Exporting structured dict format for logging/audit
    - Explanation of the score breakdown
    - Factory methods for safe construction from dict or default (empty) state
    """

    def __init__(self, regime=None, volatility=None, var=None, cvar=None, score=None):
        """
        Initialize a RiskSignalSet.

        Args:
            regime (str): Market regime, one of {"Bull", "Neutral", "Bear"}
            volatility (float): Annualized volatility estimate (e.g., from GARCH)
            var (float): Value-at-Risk (e.g., 95% daily VaR)
            cvar (float): Conditional VaR (expected shortfall)
            score (float): Optional override of computed score
        """
        self.regime = regime
        self.volatility = volatility
        self.var = var
        self.cvar = cvar
        self.score = score if score is not None else self.compute_score()

    def compute_score(self):
        """
        Compute the composite risk score from individual components using weighted sum:
        - 0.4 × regime score (Bull = +1, Bear = -1)
        - 0.25 × reverse volatility Z-score (ideal vol = 2%)
        - 0.25 × normalized VaR (target: > -3%)
        - 0.10 × normalized CVaR (target: > -4%)

        Returns:
            float: Rounded composite risk score in [-∞, +∞]
        """
        regime_score_map = {"Bull": 1, "Neutral": 0, "Bear": -1}
        regime_score = regime_score_map.get(self.regime, 0)

        vol_score = -(self.volatility - 0.02) / 0.01 if self.volatility is not None else 0
        var_score = (self.var + 0.03) / 0.01 if self.var is not None else 0
        cvar_score = (self.cvar + 0.04) / 0.015 if self.cvar is not None else 0

        total_score = (
            0.4 * regime_score +
            0.25 * vol_score +
            0.25 * var_score +
            0.10 * cvar_score
        )
        return round(total_score, 2)

    def to_dict(self, extended: bool = False) -> dict:
        """
        Export risk signal as dictionary for logging, storage, or transmission.

        Args:
            extended (bool): If True, includes timestamp and explanation metadata

        Returns:
            dict: Risk signal content
        """
        base = {
            "regime": self.regime,
            "volatility": self.volatility,
            "var": self.var,
            "cvar": self.cvar,
            "score": self.score
        }

        if extended:
            ts = get_timestamps()
            base.update({
                "generated_at": ts["ny_time_str"],
                "source_model": "RiskController.evaluate_daily_risk",
                "explanation": self._build_explanation()
            })

        return base

    def _build_explanation(self) -> str:
        """
        Build a human-readable breakdown of the score composition.

        Returns:
            str: Explanation like "0.4×regime(-1) + 0.25×vol(0.024) + ..."
        """
        parts = []
        regime_score_map = {"Bull": 1, "Neutral": 0, "Bear": -1}
        r = regime_score_map.get(self.regime, 0)

        parts.append(f"0.4×regime({r})")
        if self.volatility is not None:
            parts.append(f"0.25×vol({self.volatility:.3f})")
        if self.var is not None:
            parts.append(f"0.25×VaR({self.var:.3f})")
        if self.cvar is not None:
            parts.append(f"0.10×CVaR({self.cvar:.3f})")

        return " + ".join(parts)

    @classmethod
    def empty(cls):
        """
        Return a neutral, safe fallback signal object.
        """
        return cls(regime="Neutral", volatility=0.0, var=0.0, cvar=0.0, score=0.0)

    @classmethod
    def from_dict(cls, d):
        """
        Create RiskSignalSet from dictionary (e.g. from storage or message).

        Args:
            d (dict): Dictionary with keys for regime, volatility, var, cvar

        Returns:
            RiskSignalSet: Parsed and constructed object
        """
        if not d:
            return cls.empty()
        return cls(
            regime=d.get("regime", "Neutral"),
            volatility=d.get("volatility", 0.0),
            var=d.get("var", 0.0),
            cvar=d.get("cvar", 0.0)
        )

    def __repr__(self):
        """
        Print-friendly object representation (used in logs, debugging).
        """
        return (
            f"<RiskSignalSet R:{self.regime} "
            f"V:{self.volatility:.3f} VaR:{self.var:.3f} CVaR:{self.cvar:.3f} Score:{self.score:.2f}>"
        )

