from medbot.alert_manager import (
    build_soft_stock_alert,
    build_urgent_stock_alert,
)
from medbot.inventory_manager import (
    is_soft_alert_due,
    is_urgent_alert_due,
    reduce_stock,
)


def main():
    reduce_stock("1", "180")

    if is_urgent_alert_due("1"):
        print(build_urgent_stock_alert("1"))
    elif is_soft_alert_due("1"):
        print(build_soft_stock_alert("1"))
    else:
        print("No stock alert needed.")


if __name__ == "__main__":
    main()