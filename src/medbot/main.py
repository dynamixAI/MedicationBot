from medbot.storage import (
    append_record,
    delete_record,
    find_record,
    get_next_id,
    load_records,
    update_record,
)


MEDICATION_HEADERS = [
    "medication_id",
    "name",
    "strength",
    "dose_amount",
]


def main():
    print("Current records:")
    print(load_records("medications.csv"))

    next_id = get_next_id("medications.csv", "medication_id")
    print(f"Next ID: {next_id}")

    found = find_record("medications.csv", "medication_id", "1")
    print("Found record:")
    print(found)

    update_record(
        "medications.csv",
        "medication_id",
        "1",
        {"dose_amount": "2"},
        MEDICATION_HEADERS,
    )

    print("After update:")
    print(load_records("medications.csv"))

    append_record(
        "medications.csv",
        {
            "medication_id": get_next_id("medications.csv", "medication_id"),
            "name": "Vitamin D",
            "strength": "1000IU",
            "dose_amount": "1",
        },
        MEDICATION_HEADERS,
    )

    print("After append:")
    print(load_records("medications.csv"))

    delete_record(
        "medications.csv",
        "name",
        "Vitamin D",
        MEDICATION_HEADERS,
    )

    print("After delete:")
    print(load_records("medications.csv"))


if __name__ == "__main__":
    main()