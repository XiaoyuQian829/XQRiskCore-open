# utils/ui_utils.py

from utils.time_utils import is_market_open, get_timestamps
from datetime import datetime, timedelta
import pytz

MARKET_TZ = pytz.timezone("America/New_York")

def get_market_timing_note() -> str:
    """
    Returns a concise status line showing:
    - Market open/closed state
    - NY time
    - Local system time

    Useful for placing in dashboards.
    """
    ts = get_timestamps()
    market_open = is_market_open()

    market_status = "🟢 Open" if market_open else "🌙 Closed"
    return f"{market_status} · NY {ts['ny_time_str']} · Local {ts['local_time_str']}"


def get_dynamic_tagline(user_id: str) -> str:
    """
    Returns a personalized one-line tagline with:
    - Role-based label
    - Market timing note

    Args:
        user_id (str): Role or user identifier

    Returns:
        str: Concatenated role tagline + market time note
    """
    user_taglines = {
        "admin": "👑 System unlocked – Full access granted",
        "auditor": "🕵️ Audit trail ready. Logs don’t lie",
        "risker": "🛡️ Risk perimeter armed. Awaiting threat signals",
        "trader1": "🚀 Let’s find the trend. Stay sharp"
    }

    base = user_taglines.get(user_id, "🛡️ Secure access enabled")
    time_note = get_market_timing_note()
    return f"{base} · {time_note}"
