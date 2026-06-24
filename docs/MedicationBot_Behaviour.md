# MedicationBot Behaviour Guide

## Purpose

MedicationBot helps a user manage medications, stock, appointments, and caregiver notifications through Telegram.

The system is designed to be behaviour-driven, not hardcoded around specific medication names or fixed times.

---

## Core Principles

* No medication names are hardcoded.
* No medication times are hardcoded.
* Each medication belongs to an owner.
* Each medication can have multiple scheduled times.
* Every medication action should be logged.
* Caregiver messages must be factual and not accusatory.
* The bot should say "no confirmation received" rather than "dose not taken" unless the user explicitly marked it missed or skipped.

---

## Medication Reminder Flow

1. User adds a medication.
2. User adds one or more reminder times.
3. Scheduler builds reminder events from stored schedules.
4. At the scheduled time, the bot sends a medication reminder.
5. User can confirm taken, skip, or later be marked as missed.
6. Taken doses reduce stock.
7. All outcomes are written to medication logs.

---

## Missed Dose Flow

1. Medication is scheduled.
2. No confirmation is received.
3. After the grace period, the system marks the dose as missed.
4. A missed dose log is created.
5. The user receives a personal reminder.
6. The caregiver receives a short factual notification if caregiver alerts are enabled.

Caregiver wording:

```text
💊 Caregiver Notification

Sarah has not confirmed a scheduled medication.

Medication: Paracetamol 500mg
Scheduled: 08:00

No confirmation received.

Please check in.
```

---

## Inventory Flow

When a dose is taken:

1. Dose is logged.
2. Stock is reduced by the quantity taken.
3. Days remaining are recalculated.
4. Soft and urgent stock alerts are checked.

Daily usage is calculated as:

```text
dose_amount × number_of_daily_schedules
```

Days remaining is calculated as:

```text
stock_remaining ÷ daily_usage
```

---

## Stock Alerts

Default stock alert behaviour:

* Soft reminder: 5 days remaining
* Urgent alert: 3 days remaining

The user may accept the defaults or choose their own values.

---

## Refill Flow

If a user enters a medication that already exists:

1. Bot detects the existing medication.
2. Bot offers:

   * Add refill
   * Edit medication
   * Create new medication
3. If user chooses refill, stock is increased.
4. User can review existing strength, dose, times, and alert settings.
5. User can keep existing settings or edit them.

---

## Stock Correction Flow

Stock correction is different from refill.

* Refill adds to stock.
* Stock correction replaces stock.

Example:

```text
System stock: 116
Actual stock: 112
Correct stock to: 112
```

---

## Caregiver Management

The medication owner can:

* Add caregiver
* View caregivers
* Disable caregiver
* Reactivate caregiver
* Remove caregiver

Caregivers may be people or organisations.

Examples:

* John
* Liverpool Care Agency
* Home Support Team

---

## Appointment Flow

User enters:

* Date
* Time
* Reason
* Location

The system stores all appointments for record purposes.

Reminder defaults:

* 3 days before appointment
* 24 hours before appointment

Past appointments remain available for history.

---

## Message Template System

All user-facing and caregiver-facing messages should live in:

```text
src/medbot/message_templates.py
```

This keeps tone consistent across:

* Medication reminders
* Missed dose reminders
* Caregiver alerts
* Stock reminders
* Appointment reminders

---

## Future Telegram Flow

Telegram will act only as the interface.

Telegram commands will call existing backend functions:

```text
/addmed → medication_manager.add_medication()
/meds → medication_manager.list_medications()
/caregivers → caregiver_manager.list_caregivers()
/appointments → appointment_manager.list_appointments()
```

The medication logic should not live inside Telegram handlers.
