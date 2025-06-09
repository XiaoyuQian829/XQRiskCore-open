# core/passive/exposure_logic.py
"""
Exposure Allocation Logic
==========================

Computes target portfolio exposure weights based on risk signal inputs.
This module is designed to be pluggable and extensible for multiple exposure styles.
"""

def compute_target_exposure(signal, mode="score_based"):
    """
    Compute target asset weights based on signal and strategy mode.

    Args:
        signal (RiskSignalSet): standardized risk signals including .score
        mode (str): strategy mode ("score_based" / "regime_aware" / future custom)

    Returns:
        dict: {symbol: weight} e.g. {"SPY": 0.25, "TLT": 0.25, ...}
    """
    if signal is None or signal.score is None:
        return {}

    print(f"[⚖️] Exposure logic mode: {mode} | Score: {signal.score:.2f}")

    if mode == "score_based":
        if signal.score < -0.8:
            return {"TLT": 0.5, "QQQ": 0.2, "SPY": 0.1, "JPM": 0.2}
        elif signal.score > 0.8:
            return {"QQQ": 0.4, "SPY": 0.4, "JPM": 0.1, "TLT": 0.1}
        else:
            return {"QQQ": 0.4, "SPY": 0.1, "JPM": 0.1, "TLT": 0.4}

    # Future modes
    elif mode == "regime_aware":
        # Placeholder: add regime-specific weight mapping
        pass

    return {}
