"""
profile_manager.py

Manages user profile information.
"""

from typing import Optional

from medbot.storage import append_record, find_record, load_records, update_record


PROFILE_FILE = "user_profile.csv"

PROFILE_HEADERS = [
    "owner_id",
    "display_name",
]


def get_profile(owner_id: str = "default") -> Optional[dict[str, str]]:
    """Return profile for an owner."""
    return find_record(PROFILE_FILE, "owner_id", owner_id)


def get_display_name(owner_id: str = "default") -> Optional[str]:
    """Return display name for an owner."""
    profile = get_profile(owner_id)

    if profile is None:
        return None

    display_name = profile.get("display_name")

    if display_name:
        return display_name.title()

    return None


def create_or_update_profile(owner_id: str, display_name: str) -> dict[str, str]:
    """Create or update a user profile."""
    existing_profile = get_profile(owner_id)

    if existing_profile:
        update_record(
            PROFILE_FILE,
            "owner_id",
            owner_id,
            {"display_name": display_name},
            PROFILE_HEADERS,
        )
        return {
            "owner_id": owner_id,
            "display_name": display_name,
        }

    profile = {
        "owner_id": owner_id,
        "display_name": display_name,
    }

    append_record(PROFILE_FILE, profile, PROFILE_HEADERS)
    return profile