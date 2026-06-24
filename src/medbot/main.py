from medbot.caregiver_manager import (
    activate_caregiver,
    add_caregiver,
    deactivate_caregiver,
    list_active_caregivers,
    list_caregivers,
    remove_caregiver,
)


def main():
    print("Current caregivers:")
    print(list_caregivers())

    new_caregiver = add_caregiver(
        name="John",
        telegram_id="111222333",
    )

    print("\nAdded caregiver:")
    print(new_caregiver)

    print("\nAll caregivers:")
    print(list_caregivers())

    deactivate_caregiver(new_caregiver["caregiver_id"])

    print("\nActive caregivers after deactivate:")
    print(list_active_caregivers())

    activate_caregiver(new_caregiver["caregiver_id"])

    print("\nActive caregivers after reactivate:")
    print(list_active_caregivers())

    remove_caregiver(new_caregiver["caregiver_id"])

    print("\nAll caregivers after remove:")
    print(list_caregivers())


if __name__ == "__main__":
    main()