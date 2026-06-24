from medbot.message_templates import (
    caregiver_no_confirmation_alert,
    medication_reminder,
    missed_dose_user_reminder,
    soft_stock_alert,
    urgent_stock_alert,
)


def main():
    print(medication_reminder("Paracetamol", "500mg", "08:00"))
    print("\n---\n")

    print(missed_dose_user_reminder("Paracetamol", "500mg", "08:00"))
    print("\n---\n")

    print(caregiver_no_confirmation_alert("Sarah", "Paracetamol", "500mg", "08:00"))
    print("\n---\n")

    print(soft_stock_alert("Paracetamol", "500mg", "40", 5))
    print("\n---\n")

    print(urgent_stock_alert("Paracetamol", "500mg", "16", 2))


if __name__ == "__main__":
    main()