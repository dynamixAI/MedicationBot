from medbot.alert_manager import build_low_stock_alert
from medbot.dose_service import mark_dose_taken
from medbot.inventory_manager import get_stock


def main():
    print("Stock before:")
    print(get_stock("1"))

    result = mark_dose_taken(
        medication_id="1",
        scheduled_time="08:00",
        quantity_taken="100",
    )

    print("Dose result:")
    print(result)

    print("Stock after:")
    print(get_stock("1"))

    if result["stock_low"] == "True":
        print(build_low_stock_alert("1"))


if __name__ == "__main__":
    main()