from datetime import datetime, timedelta
import pytz
from dateutil import parser

def parse_user_date(date_str: str, tz_name: str = "UTC") -> str | None:
    text = date_str.strip().lower()
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    
    if text == "today":
        return now.strftime("%Y-%m-%d")
    elif text == "tomorrow":
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        parsed_dt = parser.parse(date_str, dayfirst=True)
        return parsed_dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def parse_user_time(time_str: str) -> str | None:
    text = time_str.strip()
    try:
        parsed_t = parser.parse(text)
        return parsed_t.strftime("%H:%M")
    except Exception:
        return None

def format_display_datetime(due_date: str, due_time: str | None) -> str:
    if not due_date:
        return "No Due Date"
    if due_time:
        return f"{due_date} at {due_time}"
    return due_date
