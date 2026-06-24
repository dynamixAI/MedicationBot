from medbot.inventory_manager import (
    add_refill,
    calculate_daily_usage,
    calculate_days_remaining,
    get_stock,
    is_soft_alert_due,
    is_urgent_alert_due,
)


def main():
    print("Stock:")
    print(get_stock("1"))

    print("Daily usage:")
    print(calculate_daily_usage("1"))

    print("Days remaining:")
    print(calculate_days_remaining("1"))

    print("Soft alert due?")
    print(is_soft_alert_due("1"))

    print("Urgent alert due?")
    print(is_urgent_alert_due("1"))

    print("Adding refill of 100...")
    add_refill("1", "100")

    print("Stock after refill:")
    print(get_stock("1"))

    print("Days remaining after refill:")
    print(calculate_days_remaining("1"))


if __name__ == "__main__":
    main()