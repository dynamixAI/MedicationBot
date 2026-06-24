"""
alert_manager.py

Creates alert messages for medication inventory and dose events.
"""

from typing import Optional

from medbot.inventory_manager import calculate_days_remaining, get_stock
from medbot.medication_manager import get_medication


def build_soft_stock_alert(medication_id: str) -> Optional[str]:
    """Build a soft stock reminder message."""
    medication = get_medication(medication_id)

    if medication is None:
        return None

    days_remaining = calculate_days_remaining(medication_id)
    stock = get_stock(medication_id)

    return (
        "💊 Prescription Reminder\n\n"
        f"Medication: {medication['name']} {medication['strength']}\n"
        f"Stock remaining: {stock}\n"
        f"Estimated days remaining: {days_remaining}\n\n"
        "You may want to order your prescription soon."
    )


def build_urgent_stock_alert(medication_id: str) -> Optional[str]:
    """Build an urgent stock alert message."""
    medication = get_medication(medication_id)

    if medication is None:
        return None

    days_remaining = calculate_days_remaining(medication_id)
    stock = get_stock(medication_id)

    return (
        "⚠️ Urgent Prescription Alert\n\n"
        f"Medication: {medication['name']} {medication['strength']}\n"
        f"Stock remaining: {stock}\n"
        f"Estimated days remaining: {days_remaining}\n\n"
        "Please order your prescription as soon as possible."
    )