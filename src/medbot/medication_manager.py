"""
medication_manager.py

Business logic for managing medications.

This layer uses storage.py but does not know anything about Telegram.
"""

from typing import Dict, List, Optional

from medbot.storage import (
    append_record,
    delete_record,
    find_record,
    get_next_id,
    load_records,
    update_record,
)


MEDICATION_FILE = "medications.csv"

MEDICATION_HEADERS = [
    "medication_id",
    "name",
    "strength",
    "dose_amount",
    "stock_remaining",
    "soft_alert_days",
    "urgent_alert_days",
    "active",
]


def list_medications() -> List[Dict[str, str]]:
    """Return all medications."""
    return load_records(MEDICATION_FILE)


def get_medication(medication_id: str) -> Optional[Dict[str, str]]:
    """Return one medication by ID."""
    return find_record(MEDICATION_FILE, "medication_id", medication_id)


def add_medication(name: str, strength: str, dose_amount: str) -> Dict[str, str]:
    """Add a new medication."""
    medication = {
        "medication_id": get_next_id(MEDICATION_FILE, "medication_id"),
        "name": name,
        "strength": strength,
        "dose_amount": dose_amount,
    }

    append_record(MEDICATION_FILE, medication, MEDICATION_HEADERS)
    return medication


def edit_medication(medication_id: str, updates: Dict[str, str]) -> bool:
    """Edit an existing medication."""
    return update_record(
        MEDICATION_FILE,
        "medication_id",
        medication_id,
        updates,
        MEDICATION_HEADERS,
    )


def remove_medication(medication_id: str) -> bool:
    """Remove a medication."""
    return delete_record(
        MEDICATION_FILE,
        "medication_id",
        medication_id,
        MEDICATION_HEADERS,
    )