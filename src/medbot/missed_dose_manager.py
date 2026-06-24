"""
missed_dose_manager.py

Detects missed medication doses.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from medbot.dose_service import mark_dose_missed
from medbot.medication_manager import get_medication


def parse_time_today(time_text: str) -> datetime:
    """Convert HH:MM text into today's datetime."""
    today = datetime.now().date()
    hour, minute = map(int, time_text.split(":"))

    return datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=hour,
        minute=minute,
    )


def is_dose_missed(
    scheduled_time: str,
    grace_minutes: int = 30,
    current_time: Optional[datetime] = None,
) -> bool:
    """Check if a dose is missed after a grace period."""
    now = current_time or datetime.now()
    scheduled_datetime = parse_time_today(scheduled_time)
    missed_after = scheduled_datetime + timedelta(minutes=grace_minutes)

    return now > missed_after


def process_missed_dose(
    medication_id: str,
    scheduled_time: str,
    grace_minutes: int = 30,
    current_time: Optional[datetime] = None,
) -> Optional[Dict[str, str]]:
    """Mark dose as missed if it is past the grace period."""
    if not is_dose_missed(scheduled_time, grace_minutes, current_time):
        return None

    return mark_dose_missed(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
    )


def build_missed_dose_alert(
    medication_id: str,
    scheduled_time: str,
) -> Optional[str]:
    """Build missed dose alert text."""
    medication = get_medication(medication_id)

    if medication is None:
        return None

    return (
    "💊 Medication Reminder\n\n"
    f"It's now more than 30 minutes since your scheduled dose of "
    f"{medication['name']} {medication['strength']} "
    f"at {scheduled_time}.\n\n"
    "If you've already taken it, please confirm it in the app.\n"
    "If not, please take your medication as prescribed."
)