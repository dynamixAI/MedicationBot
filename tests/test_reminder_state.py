"""
test_reminder_engine.py

Manual reminder engine test.
"""

from datetime import datetime

from medbot.reminder_engine import print_due_reminders


print("Testing 15 minutes before 18:00:")
print_due_reminders(datetime.fromisoformat("2026-06-26T17:45"))

print("\nTesting exact time 18:00:")
print_due_reminders(datetime.fromisoformat("2026-06-26T18:00"))

print("\nTesting 30 minutes after 18:00:")
print_due_reminders(datetime.fromisoformat("2026-06-26T18:30"))

print("\nTesting 60 minutes after 18:00:")
print_due_reminders(datetime.fromisoformat("2026-06-26T19:00"))