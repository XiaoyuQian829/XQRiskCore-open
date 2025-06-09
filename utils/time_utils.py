# utils/time_utils.py

from datetime import datetime
import pytz

# Default market timezone: Eastern Time (New York)
MARKET_TZ = pytz.timezone("America/New_York")

def get_timestamps():
    """
    Returns various formatted timestamps based on Eastern Time and local time.

    Returns:
        dict:
            - now_ny: datetime object in NY timezone
            - local_time_str: Local time as formatted string
            - ny_time_str: NY time as formatted string
            - date_str: Date string in NY timezone (YYYY-MM-DD)
    """
    now_ny = datetime.now(MARKET_TZ)
    now_local = now_ny.astimezone()  # convert to local timezone

    return {
        "now_ny": now_ny,
        "local_time_str": now_local.strftime("%Y-%m-%d %H:%M:%S"),
        "ny_time_str": now_ny.strftime("%Y-%m-%d %H:%M:%S"),
        "date_str": now_ny.strftime("%Y-%m-%d")
    }

def is_market_open(now=None):
    """
    Checks if the current time falls within standard US stock market hours
    (Monday to Friday, 9:30 AM – 4:00 PM ET).

    Args:
        now (datetime, optional): Timestamp to check. Defaults to current NY time.

    Returns:
        bool: True if within market hours, else False.
    """
    now = now or datetime.now(MARKET_TZ)
    weekday = now.weekday()
    if weekday >= 5:
        return False  # Saturday or Sunday
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

def get_local_and_market_time(market_tz_name="America/New_York"):
    """
    Returns current local and market time (as strings) along with timezone labels.

    Args:
        market_tz_name (str): IANA timezone name (e.g., "Asia/Tokyo", "Europe/London")

    Returns:
        dict:
            - local_str: Local time in HH:MM format
            - local_tz: Local timezone label
            - market_str: Market time in HH:MM format
            - market_tz: Market timezone label
    """
    local_now = datetime.now().astimezone()
    market_tz = pytz.timezone(market_tz_name)
    market_now = datetime.now(market_tz)

    return {
        "local_str": local_now.strftime("%H:%M"),
        "local_tz": local_now.tzname(),
        "market_str": market_now.strftime("%H:%M"),
        "market_tz": market_now.tzname()
    }
