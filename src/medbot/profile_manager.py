"""
profile_manager.py

Manages user profile information.
"""

from typing import Optional

from medbot.storage import load_records


PROFILE_FILE = "user_profile.csv"


def get_display_name(owner_id: str = "default") -> Optional[str]:
    """Return display name for an owner."""
    profiles = load_records(PROFILE_FILE)

    for profile in profiles:
        if profile.get("owner_id") == owner_id:
            return profile.get("display_name")

    return None