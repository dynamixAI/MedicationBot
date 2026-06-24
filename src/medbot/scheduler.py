"""
scheduler.py

Builds today's medication reminder events.
"""

from typing import Dict, List

from medbot.medication_manager import get_medication
from medbot.schedule_manager import list_schedules


def build_today_events() -> List[Dict]:
    """
    Build today's reminder events.
    """

    events = []

    schedules = list_schedules()

    for schedule in schedules:

        medication = get_medication(
            schedule["medication_id"]
        )

        if medication is None:
            continue

        events.append(
            {
                "medication_id": medication["medication_id"],
                "name": medication["name"],
                "strength": medication["strength"],
                "dose_amount": medication["dose_amount"],
                "time": schedule["time"],
            }
        )

    events.sort(
        key=lambda event: event["time"]
    )

    return events