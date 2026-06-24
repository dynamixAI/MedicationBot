from datetime import datetime

from medbot.missed_dose_manager import (
    build_missed_dose_alert,
    process_missed_dose,
)


def main():
    test_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    missed_log = process_missed_dose(
        medication_id="1",
        scheduled_time="08:00",
        grace_minutes=30,
        current_time=test_time,
    )

    if missed_log:
        print("Missed dose logged:")
        print(missed_log)
        print()
        print(build_missed_dose_alert("1", "08:00"))
    else:
        print("Dose is not missed yet.")


if __name__ == "__main__":
    main()