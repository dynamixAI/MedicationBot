from medbot.schedule_manager import add_schedule
from medbot.scheduler import build_today_events


def main():

    add_schedule("1", "08:00")
    add_schedule("1", "12:00")
    add_schedule("1", "16:00")
    add_schedule("1", "20:00")

    events = build_today_events()

    print("\nToday's Events\n")

    for event in events:
        print(
            f"{event['time']} - "
            f"{event['name']} "
            f"{event['strength']} "
            f"Take {event['dose_amount']}"
        )


if __name__ == "__main__":
    main()