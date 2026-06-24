from medbot.medication_manager import list_medications
from medbot.schedule_manager import (
    add_schedule,
    get_schedules_for_medication,
    list_schedules,
    remove_schedules_for_medication,
)


def main():
    print("Current medications:")
    print(list_medications())

    print("Adding schedules for medication 1...")
    add_schedule("1", "08:00")
    add_schedule("1", "12:00")
    add_schedule("1", "16:00")
    add_schedule("1", "20:00")

    print("All schedules:")
    print(list_schedules())

    print("Schedules for medication 1:")
    print(get_schedules_for_medication("1"))

    removed_count = remove_schedules_for_medication("1")
    print(f"Removed schedules: {removed_count}")

    print("Schedules after delete:")
    print(list_schedules())


if __name__ == "__main__":
    main()