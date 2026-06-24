"""
storage.py

Generic CSV storage layer for MedicationBot.
"""

from pathlib import Path
import csv
from typing import List, Dict


DATA_DIR = Path("data")


def ensure_file_exists(filename: str, headers: List[str]) -> None:
    """
    Create a CSV file with headers if it does not already exist.
    """

    file_path = DATA_DIR / filename

    if not file_path.exists():
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)


def load_records(filename: str) -> List[Dict]:
    """
    Load all records from a CSV file.
    """

    file_path = DATA_DIR / filename

    if not file_path.exists():
        return []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def append_record(filename: str, record: Dict) -> None:
    """
    Add a new record to a CSV file.
    """

    file_path = DATA_DIR / filename

    file_exists = file_path.exists()

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=record.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)