"""
inventory_manager.py

Handles medication stock tracking and days-remaining calculations.
"""

import math
from typing import Optional

from medbot.medication_manager import get_medication, edit_medication
from medbot.schedule_manager import get_schedules_for_medication


def get_stock(medication_id: str) -> Optional[str]:
    """Return current stock for a medication."""
    medication = get_medication(medication_id)

    if medication is None:
        return None

    return medication.get("stock_remaining")


def reduce_stock(medication_id: str, quantity_taken: str) -> bool:
    """Reduce medication stock after a dose is taken."""
    medication = get_medication(medication_id)

    if medication is None:
        return False

    current_stock = int(medication.get("stock_remaining", "0"))
    quantity = int(quantity_taken)

    new_stock = max(current_stock - quantity, 0)

    return edit_medication(
        medication_id,
        {"stock_remaining": str(new_stock)},
    )


def add_refill(medication_id: str, quantity_added: str) -> bool:
    """Add refill stock to an existing medication."""
    medication = get_medication(medication_id)

    if medication is None:
        return False

    current_stock = int(medication.get("stock_remaining", "0"))
    added = int(quantity_added)

    new_stock = current_stock + added

    return edit_medication(
        medication_id,
        {"stock_remaining": str(new_stock)},
    )

def set_stock(
    medication_id: str,
    new_stock: str,
) -> bool:
    """
    Replace stock with a corrected value.
    """

    medication = get_medication(medication_id)

    if medication is None:
        return False

    return edit_medication(
        medication_id,
        {
            "stock_remaining": str(new_stock)
        },
    )


def calculate_daily_usage(medication_id: str) -> int:
    """Calculate how many tablets/capsules are used per day."""
    medication = get_medication(medication_id)

    if medication is None:
        return 0

    dose_amount = int(medication.get("dose_amount", "0"))
    schedules = get_schedules_for_medication(medication_id)

    return dose_amount * len(schedules)


def calculate_days_remaining(medication_id: str) -> Optional[int]:
    """Calculate whole days of medication remaining."""
    medication = get_medication(medication_id)

    if medication is None:
        return None

    stock = int(medication.get("stock_remaining", "0"))
    daily_usage = calculate_daily_usage(medication_id)

    if daily_usage <= 0:
        return None

    return math.floor(stock / daily_usage)


def is_soft_alert_due(medication_id: str) -> bool:
    """Check if soft reminder is due."""
    medication = get_medication(medication_id)
    days_remaining = calculate_days_remaining(medication_id)

    if medication is None or days_remaining is None:
        return False

    soft_alert_days = int(medication.get("soft_alert_days", "5"))

    return days_remaining <= soft_alert_days


def is_urgent_alert_due(medication_id: str) -> bool:
    """Check if urgent reminder is due."""
    medication = get_medication(medication_id)
    days_remaining = calculate_days_remaining(medication_id)

    if medication is None or days_remaining is None:
        return False

    urgent_alert_days = int(medication.get("urgent_alert_days", "3"))

    return days_remaining <= urgent_alert_days