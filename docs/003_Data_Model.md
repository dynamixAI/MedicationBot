# MedicationBot Data Model v1

## medications.csv

| Field             | Description                |
| ----------------- | -------------------------- |
| medication_id     | Unique ID                  |
| name              | Medication name            |
| strength          | Medication strength        |
| dose_amount       | Number of tablets per dose |
| dose_unit         | tablet, capsule, ml        |
| stock_remaining   | Current stock              |
| reorder_threshold | Alert level                |
| active            | true/false                 |

Example

1,Paracetamol,500mg,3,tablet,120,20,true

---

## medication_schedule.csv

| Field         | Description          |
| ------------- | -------------------- |
| schedule_id   | Unique ID            |
| medication_id | Medication reference |
| time          | Reminder time        |
| active        | true/false           |

Example

1,1,08:00,true

2,1,12:00,true

3,1,16:00,true

4,1,20:00,true

---

## medication_log.csv

| Field          | Description                     |
| -------------- | ------------------------------- |
| log_id         | Unique ID                       |
| medication_id  | Medication reference            |
| scheduled_time | Scheduled reminder              |
| actual_time    | Confirmation time               |
| status         | taken, missed, snoozed, skipped |
| quantity_taken | Quantity taken                  |

Example

1,1,08:00,08:02,taken,3
