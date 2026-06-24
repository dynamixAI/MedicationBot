from medbot.inventory_manager import (
    add_refill,
    calculate_days_remaining,
    get_stock,
)


def main():
    print("Before refill:")
    print(f"Stock: {get_stock('1')}")
    print(f"Days remaining: {calculate_days_remaining('1')}")

    print("\nAdding refill of 100 tablets...")
    add_refill("1", "100")

    print("\nAfter refill:")
    print(f"Stock: {get_stock('1')}")
    print(f"Days remaining: {calculate_days_remaining('1')}")


if __name__ == "__main__":
    main()