import os
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

# Required by app.core.settings when tests import app.core.cache (via patches).
# Local runs may already have these from .env; CI does not.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("SLACK_SIGNING_SECRET", "test-signing-secret")
os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test-token")

from tests.factories import make_holiday, make_system_settings

IST = ZoneInfo("Asia/Kolkata")


@pytest.fixture
def settings():
    return make_system_settings(
        cutoff_time=time(10, 0),
        day_rollover_time=time(15, 0),
    )


@pytest.fixture
def holidays():
    return []


@pytest.fixture
def wednesday_before_cutoff():
    """Wednesday 2026-07-22 at 09:00 IST (before 10:00 cutoff)."""
    return datetime(2026, 7, 22, 9, 0, tzinfo=IST)


@pytest.fixture
def wednesday_after_cutoff():
    """Wednesday 2026-07-22 at 11:00 IST (after 10:00 cutoff)."""
    return datetime(2026, 7, 22, 11, 0, tzinfo=IST)


@pytest.fixture
def wednesday_in_waiting_list_window():
    """Wednesday 2026-07-22 at 12:00 IST (cutoff <= t < day_rollover)."""
    return datetime(2026, 7, 22, 12, 0, tzinfo=IST)


@pytest.fixture
def wednesday_after_rollover():
    """Wednesday 2026-07-22 at 16:00 IST (after day_rollover)."""
    return datetime(2026, 7, 22, 16, 0, tzinfo=IST)


@pytest.fixture
def saturday():
    """Saturday 2026-07-25 at 09:00 IST."""
    return datetime(2026, 7, 25, 9, 0, tzinfo=IST)


@pytest.fixture
def holiday_on_wednesday():
    return [make_holiday(date(2026, 7, 22), name="Test Holiday")]
