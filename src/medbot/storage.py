"""
storage.py

Generic CSV storage layer for MedicationBot.
"""

from pathlib import Path
import csv
from typing import Dict, List, Optional


DATA_DIR = Path("data")


def ensure_file_exists(filename: str, headers: List[str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    file_path = DATA_DIR / filename

    if not file_path.exists() or file_path.stat().st_size == 0:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)


def clean_record(record: Dict[str, str], headers: List[str]) -> Dict[str, str]:
    return {header: record.get(header, "") or "" for header in headers}


def load_records(filename: str) -> List[Dict[str, str]]:
    file_path = DATA_DIR / filename

    if not file_path.exists() or file_path.stat().st_size == 0:
        return []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        records = []

        for record in reader:
            record.pop(None, None)
            records.append(record)

        return records


def save_records(filename: str, records: List[Dict[str, str]], headers: List[str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    file_path = DATA_DIR / filename
    clean_records = [clean_record(record, headers) for record in records]

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(clean_records)


def append_record(filename: str, record: Dict[str, str], headers: List[str]) -> None:
    ensure_file_exists(filename, headers)
    file_path = DATA_DIR / filename
    clean = clean_record(record, headers)

    if file_path.exists() and file_path.stat().st_size > 0:
        with open(file_path, "rb+") as file:
            file.seek(-1, 2)
            last_char = file.read(1)

            if last_char != b"\n":
                file.write(b"\n")

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(clean)


def find_record(filename: str, key: str, value: str) -> Optional[Dict[str, str]]:
    for record in load_records(filename):
        if record.get(key) == value:
            return record
    return None


def get_next_id(filename: str, id_field: str) -> str:
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
    records = load_records(filename)
    original_count = len(records)

    records = [record for record in records if record.get(key) != value]

    if len(records) == original_count:
        return False

    save_records(filename, records, headers)
    return True
