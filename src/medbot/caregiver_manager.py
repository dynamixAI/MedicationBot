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
    "telegram_username",
    "telegram_chat_id",
    "active",
]


def normalize_username(username: str) -> str:
    username = username.strip()
    if not username:
        return ""
    if not username.startswith("@"):
        username = f"@{username}"
    return username.lower()


def list_caregivers(owner_id: str = "default") -> List[Dict[str, str]]:
    caregivers = load_records(CAREGIVER_FILE)
    return [c for c in caregivers if c.get("owner_id") == owner_id]


def list_active_caregivers(owner_id: str = "default") -> List[Dict[str, str]]:
    return [c for c in list_caregivers(owner_id) if c.get("active") == "true"]


def get_caregiver(caregiver_id: str) -> Optional[Dict[str, str]]:
    return find_record(CAREGIVER_FILE, "caregiver_id", caregiver_id)


def add_caregiver(
    name: str,
    telegram_username: str,
    owner_id: str = "default",
) -> Dict[str, str]:
    caregiver = {
        "owner_id": owner_id,
        "caregiver_id": get_next_id(CAREGIVER_FILE, "caregiver_id"),
        "name": name,
        "telegram_username": normalize_username(telegram_username),
        "telegram_chat_id": "",
        "active": "true",
    }

    append_record(CAREGIVER_FILE, caregiver, CAREGIVER_HEADERS)
    return caregiver


def connect_caregiver_by_username(
    telegram_username: str,
    telegram_chat_id: str,
) -> Optional[Dict[str, str]]:
    username = normalize_username(telegram_username)
    caregivers = load_records(CAREGIVER_FILE)

    for caregiver in caregivers:
        if (
            normalize_username(caregiver.get("telegram_username", "")) == username
            and caregiver.get("active") == "true"
        ):
            update_record(
                CAREGIVER_FILE,
                "caregiver_id",
                caregiver["caregiver_id"],
                {"telegram_chat_id": telegram_chat_id},
                CAREGIVER_HEADERS,
            )
            caregiver["telegram_chat_id"] = telegram_chat_id
            return caregiver

    return None


def remove_caregiver(caregiver_id: str) -> bool:
    return delete_record(
        CAREGIVER_FILE,
        "caregiver_id",
        caregiver_id,
        CAREGIVER_HEADERS,
    )