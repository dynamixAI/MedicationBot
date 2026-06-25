"""
time_parser.py

Parses flexible user time input into HH:MM format.
"""

import re
from typing import List, Optional


def parse_single_time(time_text: str) -> Optional[str]:
    """Parse flexible time input into HH:MM format."""
    text = time_text.strip().lower()
    text = text.replace(".", "")
    text = text.replace(" ", "")

    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)?", text)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = match.group(3)

    if minute < 0 or minute > 59:
        return None

    if meridiem == "am":
        if hour == 12:
            hour = 0
        elif hour < 1 or hour > 12:
            return None

    elif meridiem == "pm":
        if hour == 12:
            hour = 12
        elif 1 <= hour <= 11:
            hour += 12
        else:
            return None

    else:
        if hour < 0 or hour > 23:
            return None

    return f"{hour:02d}:{minute:02d}"


def parse_time_list(times_text: str) -> Optional[List[str]]:
    """Parse comma-separated flexible times."""
    parts = [item.strip() for item in times_text.split(",") if item.strip()]

    if not parts:
        return None

    parsed_times = []

    for part in parts:
        parsed = parse_single_time(part)

        if parsed is None:
            return None

        parsed_times.append(parsed)

    return parsed_times


def recommend_times(times_per_day: int) -> List[str]:
    """Recommend reminder times based on daily frequency."""
    recommendations = {
        1: ["08:00"],
        2: ["08:00", "20:00"],
        3: ["08:00", "14:00", "20:00"],
        4: ["08:00", "12:00", "16:00", "20:00"],
    }

    return recommendations.get(times_per_day, [])