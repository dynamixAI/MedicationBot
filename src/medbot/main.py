from medbot.log_manager import list_logs, record_medication_event


def main():
    log = record_medication_event(
        medication_id="1",
        scheduled_time="08:00",
        status="taken",
        quantity_taken="2",
    )

    print("New log:")
    print(log)

    print("All logs:")
    print(list_logs())


if __name__ == "__main__":
    main()