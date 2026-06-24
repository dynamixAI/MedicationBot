"""
storage.py

Generic CSV storage layer for MedicationBot.

This module handles low-level CSV operations:
- load records
- append records
- find records
- update records
- delete records
- generate next IDs

The rest of the app should use this layer instead of reading/writing CSV directly.
"""

from pathlib import Path
import csv
from typing import Dict, List, Optional


DATA_DIR = Path("data")


def ensure_file_exists(filename: str, headers: List[str]) -> None:
    """Create a CSV file with headers if it does not already exist."""
    file_path = DATA_DIR / filename

    if not file_path.exists() or file_path.stat().st_size == 0:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)


def load_records(filename: str) -> List[Dict[str, str]]:
    """Load all records from a CSV file."""
    file_path = DATA_DIR / filename

    if not file_path.exists() or file_path.stat().st_size == 0:
        return []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_records(filename: str, records: List[Dict[str, str]], headers: List[str]) -> None:
    """Save all records to a CSV file, replacing existing content."""
    file_path = DATA_DIR / filename

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)


def append_record(filename: str, record: Dict[str, str], headers: List[str]) -> None:
    """Add a new record to a CSV file."""
    ensure_file_exists(filename, headers)

    file_path = DATA_DIR / filename

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(record)


def find_record(filename: str, key: str, value: str) -> Optional[Dict[str, str]]:
    """Find a single record where key equals value."""
    records = load_records(filename)

    for record in records:
        if record.get(key) == value:
            return record

    return None


def get_next_id(filename: str, id_field: str) -> str:
    """Get the next numeric ID for a CSV file."""
    records = load_records(filename)

    if not records:
        return "1"

    max_id = 0

    for record in records:
        try:
            current_id = int(record.get(id_field, "0"))
            max_id = max(max_id, current_id)
        except ValueError:
            continue

    return str(max_id + 1)


def update_record(
    filename: str,
    key: str,
    value: str,
    updates: Dict[str, str],
    headers: List[str],
) -> bool:
    """Update a record where key equals value."""
    records = load_records(filename)
    updated = False

    for record in records:
        if record.get(key) == value:
            record.update(updates)
            updated = True
            break

    if updated:
        save_records(filename, records, headers)

    return updated


def delete_record(
    filename: str,
    key: str,
    value: str,
    headers: List[str],
) -> bool:
    """Delete a record where key equals value."""
    records = load_records(filename)
    original_count = len(records)

    records = [record for record in records if record.get(key) != value]

    if len(records) == original_count:
        return False

    save_records(filename, records, headers)
    return True