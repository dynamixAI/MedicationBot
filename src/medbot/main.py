from medbot.inventory_manager import (
    get_stock,
    set_stock,
    calculate_days_remaining,
)


def main():

    print("Current stock:")
    print(get_stock("1"))

    print("\nCorrecting stock to 112...")

    set_stock(
        medication_id="1",
        new_stock="112",
    )

    print("\nUpdated stock:")
    print(get_stock("1"))

    print("\nDays remaining:")
    print(calculate_days_remaining("1"))


if __name__ == "__main__":
    main()