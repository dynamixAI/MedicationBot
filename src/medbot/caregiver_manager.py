"""
caregiver_manager.py

Manages approved caregivers.
"""

from typing import Dict, List

from medbot.storage import load_records


CAREGIVER_FILE = "caregivers.csv"


def list_caregivers(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return active caregivers for an owner."""
    caregivers = load_records(CAREGIVER_FILE)

    return [
        caregiver
        for caregiver in caregivers
        if caregiver.get("owner_id") == owner_id
        and caregiver.get("active") == "true"
    ]