# utils/risk_utils.py

import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
from hmmlearn.hmm import GaussianHMM
from arch import arch_model

# === VaR & CVaR ===

def calculate_var(prices: pd.DataFrame, now: datetime, lookback_days: int = 50, confidence_level: float = 0.95) -> float:
    if "date" in prices.columns:
        prices["date"] = pd.to_datetime(prices["date"])
        prices = prices.set_index("date").sort_index()

    if "close" not in prices.columns or len(prices) < lookback_days:
        print("⚠️ Not enough data to compute VaR")
        return np.nan

    close = prices["close"].iloc[-lookback_days:]
    returns = np.log(close / close.shift(1)).dropna()

    if returns.empty:
        return np.nan

    sorted_returns = np.sort(returns)
    index = int((1 - confidence_level) * len(sorted_returns))
    return float(sorted_returns[index])


def calculate_cvar(prices: pd.DataFrame, now: datetime, lookback_days: int = 50, confidence_level: float = 0.95) -> float:
    if "date" in prices.columns:
        prices["date"] = pd.to_datetime(prices["date"])
        prices = prices.set_index("date").sort_index()

    if "close" not in prices.columns or len(prices) < lookback_days:
        print("⚠️ Not enough data to compute CVaR")
        return np.nan

    close = prices["close"].iloc[-lookback_days:]
    returns = np.log(close / close.shift(1)).dropna()
    var = calculate_var(prices, now, lookback_days, confidence_level)

    if np.isnan(var):
        return np.nan

    losses = returns[returns <= var]
    return float(losses.mean()) if not losses.empty else var


# === Volatility: GARCH ===

def predict_garch(prices: pd.DataFrame, now: datetime, lookback_days: int = 50) -> float:
    if "date" in prices.columns:
        prices["date"] = pd.to_datetime(prices["date"], utc=True)
        prices = prices.set_index("date").sort_index()

    if "close" not in prices.columns or len(prices) < lookback_days:
        print("⚠️ Not enough data to compute GARCH volatility.")
        return np.nan

    close = prices["close"].iloc[-lookback_days:]
    log_returns = 100 * np.log(close / close.shift(1)).dropna()

    try:
        model = arch_model(log_returns, vol='Garch', p=1, q=1)
        model_fit = model.fit(disp="off")
        forecast = model_fit.forecast(horizon=1)
        predicted_vol = np.sqrt(forecast.variance.values[-1, -1]) / 100
        return float(predicted_vol)
    except Exception as e:
        print(f"⚠️ GARCH model fitting failed: {e}")
        return np.nan


# === Regime Detection: HMM ===

def detect_regime(price_series: pd.Series, n_states: int = 3, lambda_decay: float = 0.1) -> pd.Series:
    log_returns = np.log(price_series / price_series.shift(1)).dropna()
    log_returns = log_returns.replace([np.inf, -np.inf], np.nan).dropna()

    if len(log_returns) < 30:
        return pd.Series(index=price_series.index[1:], data="Neutral")

    X = log_returns.values.reshape(-1, 1)

    try:
        model = GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000, random_state=42)
        model.fit(X)
        hidden_states = model.predict(X)
    except Exception as e:
        print(f"⚠️ HMM fitting failed: {e}")
        return pd.Series(index=log_returns.index, data="Neutral")

    state_means = model.means_.flatten()
    sorted_states = np.argsort(state_means)
    regime_map = {
        sorted_states[2]: "Bull",
        sorted_states[1]: "Neutral",
        sorted_states[0]: "Bear"
    }

    regimes = pd.Series(hidden_states, index=log_returns.index)
    return regimes.map(regime_map)


def get_regime_today(prices: pd.DataFrame, now: datetime, lambda_decay: float = 0.1) -> str:
    if "date" in prices.columns:
        prices["date"] = pd.to_datetime(prices["date"])
        prices = prices.set_index("date").sort_index()

    if "close" not in prices.columns or len(prices) < 51:
        return "Neutral"

    close_series = prices["close"].iloc[-51:-1]
    regime_series = detect_regime(close_series, lambda_decay=lambda_decay)
    if regime_series.empty:
        return "Neutral"

    weights = defaultdict(float)
    for t, r in enumerate(regime_series):
        weight = np.exp(-lambda_decay * (len(regime_series) - 1 - t))
        weights[r] += weight

    return max(weights.items(), key=lambda x: x[1])[0]


def get_regime_proba(prices: pd.DataFrame, now: datetime, lambda_decay: float = 0.1) -> dict:
    if "date" in prices.columns:
        prices["date"] = pd.to_datetime(prices["date"])
        prices = prices.set_index("date").sort_index()

    if "close" not in prices.columns:
        return {"Bull": 0.33, "Neutral": 0.34, "Bear": 0.33}

    close_series = prices["close"]
    log_returns = np.log(close_series / close_series.shift(1)).dropna()
    log_returns = log_returns.replace([np.inf, -np.inf], np.nan).dropna()

    if len(log_returns) < 30:
        return {"Bull": 0.33, "Neutral": 0.34, "Bear": 0.33}

    X = log_returns.values.reshape(-1, 1)

    try:
        model = GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
        model.fit(X)
        probs = model.predict_proba(X)
    except Exception as e:
        print(f"⚠️ HMM proba prediction failed: {e}")
        return {"Bull": 0.33, "Neutral": 0.34, "Bear": 0.33}

    last_probs = probs[-1]
    state_means = model.means_.flatten()
    sorted_states = np.argsort(state_means)
    state_to_regime = {
        sorted_states[2]: "Bull",
        sorted_states[1]: "Neutral",
        sorted_states[0]: "Bear"
    }

    return {state_to_regime[i]: float(last_probs[i]) for i in range(3)}
