"""
appointment_manager.py

Manages appointments and appointment reminders.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from medbot.storage import (
    append_record,
    delete_record,
    find_record,
    get_next_id,
    load_records,
    update_record,
)


APPOINTMENT_FILE = "appointments.csv"

APPOINTMENT_HEADERS = [
    "owner_id",
    "appointment_id",
    "date",
    "time",
    "reason",
    "location",
    "active",
]


def list_appointments(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return all appointments for an owner."""
    appointments = load_records(APPOINTMENT_FILE)

    return [
        appointment
        for appointment in appointments
        if appointment.get("owner_id") == owner_id
    ]


def get_appointment(appointment_id: str) -> Optional[Dict[str, str]]:
    """Return one appointment by ID."""
    return find_record(APPOINTMENT_FILE, "appointment_id", appointment_id)


def add_appointment(
    date: str,
    time: str,
    reason: str,
    location: str,
    owner_id: str = "default",
) -> Dict[str, str]:
    """Add an appointment."""
    appointment = {
        "owner_id": owner_id,
        "appointment_id": get_next_id(APPOINTMENT_FILE, "appointment_id"),
        "date": date,
        "time": time,
        "reason": reason,
        "location": location,
        "active": "true",
    }

    append_record(APPOINTMENT_FILE, appointment, APPOINTMENT_HEADERS)
    return appointment


def edit_appointment(
    appointment_id: str,
    updates: Dict[str, str],
) -> bool:
    """Edit an appointment."""
    return update_record(
        APPOINTMENT_FILE,
        "appointment_id",
        appointment_id,
        updates,
        APPOINTMENT_HEADERS,
    )


def remove_appointment(appointment_id: str) -> bool:
    """Remove an appointment."""
    return delete_record(
        APPOINTMENT_FILE,
        "appointment_id",
        appointment_id,
        APPOINTMENT_HEADERS,
    )


def appointment_datetime(appointment: Dict[str, str]) -> datetime:
    """Convert appointment date and time into datetime."""
    return datetime.strptime(
        f"{appointment['date']} {appointment['time']}",
        "%Y-%m-%d %H:%M",
    )


def list_upcoming_appointments(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return upcoming active appointments."""
    now = datetime.now()

    appointments = [
        appointment
        for appointment in list_appointments(owner_id)
        if appointment.get("active") == "true"
        and appointment_datetime(appointment) >= now
    ]

    return sorted(appointments, key=appointment_datetime)


def list_past_appointments(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return past appointments for record purposes."""
    now = datetime.now()

    appointments = [
        appointment
        for appointment in list_appointments(owner_id)
        if appointment_datetime(appointment) < now
    ]

    return sorted(appointments, key=appointment_datetime, reverse=True)


def reminder_due(
    appointment: Dict[str, str],
    reminder_hours_before: int,
    current_time: Optional[datetime] = None,
) -> bool:
    """Check if an appointment reminder is due."""
    now = current_time or datetime.now()
    appointment_time = appointment_datetime(appointment)
    reminder_time = appointment_time - timedelta(hours=reminder_hours_before)

    return now >= reminder_time and now < appointment_time