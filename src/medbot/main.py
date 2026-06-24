from medbot.caregiver_manager import list_caregivers
from medbot.missed_dose_manager import build_caregiver_missed_dose_alert


def main():
    print("Active caregivers:")
    print(list_caregivers("default"))

    print("\nCaregiver alert:")
    print(build_caregiver_missed_dose_alert("1", "08:00"))


if __name__ == "__main__":
    main()