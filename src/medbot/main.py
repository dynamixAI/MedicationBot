from medbot.storage import (
    ensure_file_exists,
    append_record,
    load_records
)


def main():

    ensure_file_exists(
        "medications.csv",
        [
            "medication_id",
            "name",
            "strength",
            "dose_amount"
        ]
    )

   # append_record(
    #    "medications.csv",
     #   {
      #      "medication_id": "1",
       #     "name": "Paracetamol",
        #    "strength": "500mg",
         #   "dose_amount": "3"
        #}
    #)

    records = load_records("medications.csv")

    print(records)


if __name__ == "__main__":
    main()