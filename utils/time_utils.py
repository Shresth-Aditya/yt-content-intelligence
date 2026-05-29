from datetime import (
    datetime,
    time as datetime_time,
    timedelta
)
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

def get_previous_day_window():
    """
    Build a closed IST daily window:
    yesterday 12 AM IST <= published_at < today 12 AM IST.
    """

    today_ist = datetime.now(IST).date()
    logical_date = today_ist - timedelta(days=1)

    window_start_ist = datetime.combine(
        logical_date,
        datetime_time.min,
        tzinfo=IST
    )
    window_end_ist = window_start_ist + timedelta(days=1)

    return {
        "logical_date": logical_date.isoformat(),
        "published_after": window_start_ist.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "published_before": window_end_ist.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def get_snapshot_date():
    return datetime.now(IST).date().isoformat()

def get_snapshot_time():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
