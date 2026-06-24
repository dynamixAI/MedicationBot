from medbot.medication_manager import (
    add_medication,
    edit_medication,
    get_medication,
    list_medications,
    remove_medication,
)


def main():
    print("Current medications:")
    print(list_medications())

    new_med = add_medication("Vitamin D", "1000IU", "1")
    print("Added medication:")
    print(new_med)

    print("After add:")
    print(list_medications())

    edit_medication(new_med["medication_id"], {"dose_amount": "2"})
    print("After edit:")
    print(get_medication(new_med["medication_id"]))

    remove_medication(new_med["medication_id"])
    print("After delete:")
    print(list_medications())


if __name__ == "__main__":
    main()