"""
dose_service.py

Handles medication dose actions.

When a dose is taken:
- record it in medication_log.csv
- reduce stock
- check low stock
"""

from typing import Dict

from medbot.inventory_manager import get_stock, is_stock_low, reduce_stock
from medbot.log_manager import record_medication_event


def mark_dose_taken(
    medication_id: str,
    scheduled_time: str,
    quantity_taken: str,
) -> Dict[str, str]:
    """Mark a medication dose as taken."""
    log = record_medication_event(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        status="taken",
        quantity_taken=quantity_taken,
    )

    reduce_stock(medication_id, quantity_taken)

    log["stock_remaining"] = get_stock(medication_id)
    log["stock_low"] = str(is_stock_low(medication_id))

    return log


def mark_dose_missed(
    medication_id: str,
    scheduled_time: str,
) -> Dict[str, str]:
    """Mark a medication dose as missed."""
    return record_medication_event(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        status="missed",
        quantity_taken="0",
    )


def mark_dose_skipped(
    medication_id: str,
    scheduled_time: str,
) -> Dict[str, str]:
    """Mark a medication dose as skipped."""
    return record_medication_event(
        medication_id=medication_id,
        scheduled_time=scheduled_time,
        status="skipped",
        quantity_taken="0",
    )