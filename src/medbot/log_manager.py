"""
log_manager.py

Records medication reminder outcomes:
- taken
- missed
- skipped
- snoozed
"""

from datetime import datetime
from typing import Dict, List

from medbot.storage import append_record, get_next_id, load_records


LOG_FILE = "medication_log.csv"

LOG_HEADERS = [
    "log_id",
    "medication_id",
    "scheduled_time",
    "actual_time",
    "status",
    "quantity_taken",
]


def list_logs() -> List[Dict[str, str]]:
    """Return all medication logs."""
    return load_records(LOG_FILE)


def record_medication_event(
    medication_id: str,
    scheduled_time: str,
    status: str,
    quantity_taken: str = "0",
) -> Dict[str, str]:
    """Record a medication event."""
    log = {
        "log_id": get_next_id(LOG_FILE, "log_id"),
        "medication_id": medication_id,
        "scheduled_time": scheduled_time,
        "actual_time": datetime.now().strftime("%H:%M"),
        "status": status,
        "quantity_taken": quantity_taken,
    }

    append_record(LOG_FILE, log, LOG_HEADERS)
    return log