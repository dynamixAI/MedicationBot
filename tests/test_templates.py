from medbot.message_templates import (
    caregiver_no_confirmation_alert,
    medication_reminder,
    missed_dose_user_reminder,
    soft_stock_alert,
    urgent_stock_alert,
)


print(medication_reminder("Paracetamol", "500mg", "08:00"))
print("---")
print(missed_dose_user_reminder("Paracetamol", "500mg", "08:00"))
print("---")
print(caregiver_no_confirmation_alert("Sarah", "Paracetamol", "500mg", "08:00"))
print("---")
print(soft_stock_alert("Paracetamol", "500mg", "40", 5))
print("---")
print(urgent_stock_alert("Paracetamol", "500mg", "16", 2))