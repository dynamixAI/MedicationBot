from datetime import datetime

from medbot.appointment_manager import (
    add_appointment,
    list_past_appointments,
    list_upcoming_appointments,
    reminder_due,
)
from medbot.message_templates import appointment_reminder


def main():
    appointment = add_appointment(
        date="2026-07-01",
        time="10:30",
        reason="GP appointment",
        location="Town Centre Medical Practice",
    )

    print("Added appointment:")
    print(appointment)

    print("\nUpcoming appointments:")
    print(list_upcoming_appointments())

    print("\nPast appointments:")
    print(list_past_appointments())

    test_time = datetime(2026, 6, 28, 10, 30)

    if reminder_due(appointment, 72, test_time):
        print("\n3-day reminder:")
        print(
            appointment_reminder(
                appointment["reason"],
                appointment["date"],
                appointment["time"],
                appointment["location"],
                "3 days before",
            )
        )

    test_time = datetime(2026, 6, 30, 10, 30)

    if reminder_due(appointment, 24, test_time):
        print("\n24-hour reminder:")
        print(
            appointment_reminder(
                appointment["reason"],
                appointment["date"],
                appointment["time"],
                appointment["location"],
                "24 hours before",
            )
        )


if __name__ == "__main__":
    main()