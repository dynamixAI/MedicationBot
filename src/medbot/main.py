from medbot.inventory_manager import get_stock, is_stock_low, reduce_stock


def main():
    print("Stock before:")
    print(get_stock("1"))

    reduce_stock("1", "2")

    print("Stock after:")
    print(get_stock("1"))

    print("Is stock low?")
    print(is_stock_low("1"))


if __name__ == "__main__":
    main()