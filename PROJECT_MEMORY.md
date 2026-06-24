# MedicationBot - Project Memory

## Project Purpose

MedicationBot is a Telegram-based healthcare assistant designed to help users manage:

* Medication reminders
* Medication inventory
* Appointment reminders
* Caregiver notifications
* Medication compliance reporting

## Design Principles

1. Behaviour-driven architecture
2. Event-driven scheduling
3. No hardcoded medication names
4. No hardcoded medication times
5. Storage-independent design
6. CSV first, SQLite later
7. Telegram is the interface, not the business logic

## Architecture

Telegram User

↓

Telegram Interface Layer

↓

Business Logic Layer

↓

Scheduler Layer

↓

Storage Layer

↓

CSV Storage (v1)

↓

SQLite Storage (v2)

## Current Phase

Sprint 1 - Foundation

## Completed

* GitHub repository created
* Codespaces configured
* Python environment verified
* Project structure created

## Next Task

Create CSV storage engine.

## Future Milestones

Sprint 2

* CSV Storage Layer

Sprint 3

* Medication CRUD

Sprint 4

* Reminder Scheduler

Sprint 5

* Inventory Management

Sprint 6

* Caregiver Notifications

Sprint 7

* Reports and Analytics

Sprint 8

* SQLite Migration

## Coding Rules

* Use type hints.
* Write docstrings.
* Keep functions small.
* Avoid duplicated logic.
* Log all medication actions.
* Build reusable components.
