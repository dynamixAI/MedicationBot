"""
message_templates.py

Central place for all user-facing and caregiver-facing messages.
"""


def medication_reminder(
    medication_name: str,
    strength: str,
    scheduled_time: str,
) -> str:
    """Reminder sent to the medication user."""
    return (
        "💊 Medication Reminder\n\n"
        f"It's time for your scheduled dose of "
        f"{medication_name} {strength} at {scheduled_time}.\n\n"
        "Please confirm once taken."
    )


def missed_dose_user_reminder(
    medication_name: str,
    strength: str,
    scheduled_time: str,
    grace_minutes: int = 30,
) -> str:
    """Reminder sent to user when dose is overdue."""
    return (
        "💊 Medication Reminder\n\n"
        f"It's now more than {grace_minutes} minutes since your scheduled dose of "
        f"{medication_name} {strength} at {scheduled_time}.\n\n"
        "If you've already taken it, please confirm it in the app.\n"
        "If not, please take your medication as prescribed."
    )


def caregiver_no_confirmation_alert(
    display_name: str,
    medication_name: str,
    strength: str,
    scheduled_time: str,
) -> str:
    """Caregiver alert when no confirmation has been received."""
    return (
        "💊 Caregiver Notification\n\n"
        f"{display_name} has not confirmed a scheduled medication.\n\n"
        f"Medication: {medication_name} {strength}\n"
        f"Scheduled: {scheduled_time}\n\n"
        "No confirmation received.\n\n"
        "Please check in."
    )


def soft_stock_alert(
    medication_name: str,
    strength: str,
    stock_remaining: str,
    days_remaining: int,
) -> str:
    """Soft prescription reminder."""
    return (
        "💊 Prescription Reminder\n\n"
        f"Medication: {medication_name} {strength}\n"
        f"Stock remaining: {stock_remaining}\n"
        f"Estimated days remaining: {days_remaining}\n\n"
        "You may want to order your prescription soon."
    )


def urgent_stock_alert(
    medication_name: str,
    strength: str,
    stock_remaining: str,
    days_remaining: int,
) -> str:
    """Urgent prescription reminder."""
    return (
        "⚠️ Urgent Prescription Alert\n\n"
        f"Medication: {medication_name} {strength}\n"
        f"Stock remaining: {stock_remaining}\n"
        f"Estimated days remaining: {days_remaining}\n\n"
        "Please order your prescription as soon as possible."
    )

def appointment_reminder(
    reason: str,
    date: str,
    time: str,
    location: str,
    reminder_label: str,
) -> str:
    """Appointment reminder message."""
    return (
        f"📅 Appointment Reminder - {reminder_label}\n\n"
        f"Reason: {reason}\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Location: {location}"
    )


def welcome_message(display_name: str | None = None) -> str:
    """Build the MediBot welcome message."""

    if display_name:
        return (
            f"💊 Welcome back, {display_name}!\n\n"
            "I'm ready to help you manage:\n\n"
            "💊 Medications\n"
            "📅 Appointments\n"
            "👥 Caregivers\n"
            "📦 Prescription stock\n"
            "🔔 Reminders\n\n"
            "Type /help whenever you need assistance."
        )

    return (
        "💊 Welcome to MediBot!\n\n"
        "Your personal medication and health companion.\n\n"
        "I can help you manage:\n\n"
        "💊 Medications\n"
        "📅 Appointments\n"
        "👥 Caregivers\n"
        "📦 Prescription stock\n"
        "🔔 Reminders\n\n"
        "Type /help to get started."
    )