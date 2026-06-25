"""
medication_manager.py

Business logic for managing medications.
"""

from typing import Dict, List, Optional

from medbot.storage import (
    append_record,
    delete_record,
    get_next_id,
    load_records,
    update_record,
)


MEDICATION_FILE = "medications.csv"

MEDICATION_HEADERS = [
    "owner_id",
    "medication_id",
    "name",
    "strength",
    "dose_amount",
    "stock_remaining",
    "soft_alert_days",
    "urgent_alert_days",
    "active",
]


def list_medications(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return all active medications for an owner."""
    medications = load_records(MEDICATION_FILE)

    return [
        medication
        for medication in medications
        if medication.get("owner_id") == owner_id
        and medication.get("active") == "true"
    ]


def get_medication(
    medication_id: str,
    owner_id: str = "default",
) -> Optional[Dict[str, str]]:
    """Return one medication by ID for an owner."""
    for medication in list_medications(owner_id):
        if medication.get("medication_id") == medication_id:
            return medication

    return None


def add_medication(
    name: str,
    strength: str,
    dose_amount: str,
    stock_remaining: str,
    owner_id: str = "default",
    soft_alert_days: str = "5",
    urgent_alert_days: str = "3",
) -> Dict[str, str]:
    """Add a new medication."""
    medication = {
        "owner_id": owner_id,
        "medication_id": get_next_id(MEDICATION_FILE, "medication_id"),
        "name": name,
        "strength": strength,
        "dose_amount": dose_amount,
        "stock_remaining": stock_remaining,
        "soft_alert_days": soft_alert_days,
        "urgent_alert_days": urgent_alert_days,
        "active": "true",
    }

    append_record(MEDICATION_FILE, medication, MEDICATION_HEADERS)
    return medication


def edit_medication(
    medication_id: str,
    updates: Dict[str, str],
) -> bool:
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


def find_medication_by_name_and_strength(
    name: str,
    strength: str,
    owner_id: str = "default",
) -> Optional[Dict[str, str]]:
    """Find an existing medication by name and strength."""
    for medication in list_medications(owner_id):
        if (
            medication.get("name", "").lower() == name.lower()
            and medication.get("strength", "").lower() == strength.lower()
        ):
            return medication

    return None