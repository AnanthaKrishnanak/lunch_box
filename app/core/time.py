from datetime import date, datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def now() -> datetime:
    """Return current time in IST."""
    return datetime.now(IST)


def today() -> date:
    """Return current date in IST."""
    return now().date()
