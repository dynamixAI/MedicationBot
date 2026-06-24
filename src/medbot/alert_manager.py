"""
alert_manager.py

Creates alert messages for medication events.
"""

from typing import Optional

from medbot.medication_manager import get_medication


def build_low_stock_alert(medication_id: str) -> Optional[str]:
    """Build a low-stock alert message for a medication."""
    medication = get_medication(medication_id)

    if medication is None:
        return None

    name = medication["name"]
    strength = medication["strength"]
    stock = medication.get("stock_remaining", "0")
    threshold = medication.get("reorder_threshold", "0")

    return (
        "⚠️ Low Stock Alert\n\n"
        f"Medication: {name} {strength}\n"
        f"Stock remaining: {stock}\n"
        f"Reorder threshold: {threshold}\n\n"
        "Please order your prescription."
    )