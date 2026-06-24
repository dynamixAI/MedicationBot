"""
caregiver_manager.py

Manages approved caregivers.
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


CAREGIVER_FILE = "caregivers.csv"

CAREGIVER_HEADERS = [
    "owner_id",
    "caregiver_id",
    "name",
    "telegram_id",
    "active",
]


def list_caregivers(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return all caregivers for an owner."""
    caregivers = load_records(CAREGIVER_FILE)

    return [
        caregiver
        for caregiver in caregivers
        if caregiver.get("owner_id") == owner_id
    ]


def list_active_caregivers(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return active caregivers for an owner."""
    return [
        caregiver
        for caregiver in list_caregivers(owner_id)
        if caregiver.get("active") == "true"
    ]


def get_caregiver(caregiver_id: str) -> Optional[Dict[str, str]]:
    """Return one caregiver by ID."""
    return find_record(CAREGIVER_FILE, "caregiver_id", caregiver_id)


def add_caregiver(
    name: str,
    telegram_id: str,
    owner_id: str = "default",
) -> Dict[str, str]:
    """Add a caregiver."""
    caregiver = {
        "owner_id": owner_id,
        "caregiver_id": get_next_id(CAREGIVER_FILE, "caregiver_id"),
        "name": name,
        "telegram_id": telegram_id,
        "active": "true",
    }

    append_record(CAREGIVER_FILE, caregiver, CAREGIVER_HEADERS)
    return caregiver


def remove_caregiver(caregiver_id: str) -> bool:
    """Remove a caregiver."""
    return delete_record(
        CAREGIVER_FILE,
        "caregiver_id",
        caregiver_id,
        CAREGIVER_HEADERS,
    )


def deactivate_caregiver(caregiver_id: str) -> bool:
    """Deactivate a caregiver without deleting them."""
    return update_record(
        CAREGIVER_FILE,
        "caregiver_id",
        caregiver_id,
        {"active": "false"},
        CAREGIVER_HEADERS,
    )


def activate_caregiver(caregiver_id: str) -> bool:
    """Reactivate a caregiver."""
    return update_record(
        CAREGIVER_FILE,
        "caregiver_id",
        caregiver_id,
        {"active": "true"},
        CAREGIVER_HEADERS,
    )