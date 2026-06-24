"""
inventory_manager.py

Handles medication stock tracking.
"""

from typing import Dict, Optional

from medbot.medication_manager import get_medication, edit_medication


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


def is_stock_low(medication_id: str) -> bool:
    """Check if medication stock is at or below reorder threshold."""
    medication = get_medication(medication_id)

    if medication is None:
        return False

    stock = int(medication.get("stock_remaining", "0"))
    threshold = int(medication.get("reorder_threshold", "0"))

    return stock <= threshold