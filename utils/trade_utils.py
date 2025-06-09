# utils/trade_utils.py

def simulate_slippage(executed_price: float, expected_price: float) -> float:
    """
    Calculate slippage percentage:
    - Positive → executed price is higher than expected (buy-side slippage)
    - Negative → executed price is lower than expected (favorable or sell-side slippage)
    
    Args:
        executed_price (float): Actual executed trade price
        expected_price (float): Intended/expected trade price

    Returns:
        float: Slippage as a percentage (rounded to 4 decimals)
    """
    if expected_price == 0:
        return 0.0  # Avoid division by zero
    return round((executed_price - expected_price) / expected_price * 100, 4)


def estimate_commission(symbol: str, quantity: int, price: float, broker: str = "generic") -> float:
    """
    Estimate trade commission based on broker model:
    - Supports flat-rate or percentage-based models
    - Easily extendable for ETFs, options, or exchange-specific pricing

    Args:
        symbol (str): Ticker symbol
        quantity (int): Number of shares
        price (float): Price per share
        broker (str): Commission model (e.g., 'generic', 'free', 'percent')

    Returns:
        float: Estimated commission in dollars
    """
    if broker == "generic":
        cost_per_share = 0.005  # $0.005 per share
        commission = quantity * cost_per_share
        return round(max(commission, 1.0), 4)  # Minimum $1

    elif broker == "free":
        return 0.0  # Commission-free broker (e.g., Robinhood)

    elif broker == "percent":
        commission = quantity * price * 0.001  # 0.1% of trade value
        return round(max(commission, 1.0), 4)

    else:
        # Unknown broker model → default to $0
        return 0.0
