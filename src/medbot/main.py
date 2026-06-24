from medbot.dose_service import mark_dose_taken, mark_dose_missed
from medbot.inventory_manager import get_stock


def main():
    print("Stock before:")
    print(get_stock("1"))

    taken_log = mark_dose_taken(
        medication_id="1",
        scheduled_time="08:00",
        quantity_taken="2",
    )

    print("Taken log:")
    print(taken_log)

    print("Stock after taken:")
    print(get_stock("1"))

    missed_log = mark_dose_missed(
        medication_id="1",
        scheduled_time="12:00",
    )

    print("Missed log:")
    print(missed_log)


if __name__ == "__main__":
    main()