from medbot.medication_manager import find_medication_by_name_and_strength


def main():
    medication = find_medication_by_name_and_strength(
        "Paracetamol",
        "500mg",
    )

    if medication:
        print("Medication already exists:")
        print(medication)
        print("\nOptions:")
        print("1. Add refill")
        print("2. Edit medication")
        print("3. Create new medication")
    else:
        print("Medication does not exist. Create new medication.")


if __name__ == "__main__":
    main()