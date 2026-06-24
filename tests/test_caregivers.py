from medbot.caregiver_manager import (
    activate_caregiver,
    add_caregiver,
    deactivate_caregiver,
    list_active_caregivers,
    list_caregivers,
    remove_caregiver,
)


print("Current caregivers:")
print(list_caregivers())

new_caregiver = add_caregiver("Test Person", "999888777")
print("Added:")
print(new_caregiver)

print("All:")
print(list_caregivers())

deactivate_caregiver(new_caregiver["caregiver_id"])
print("Active after deactivate:")
print(list_active_caregivers())

activate_caregiver(new_caregiver["caregiver_id"])
print("Active after activate:")
print(list_active_caregivers())

remove_caregiver(new_caregiver["caregiver_id"])
print("After remove:")
print(list_caregivers())