"""
medication_handler.py

Router for medication screens and flows.
"""

from telegram import Update
from telegram.ext import ContextTypes

from medbot.handlers.medication.add_flow import (
    handle_add_medication_text,
    start_add_medication,
)
from medbot.handlers.medication.list_screen import show_medications_screen
from medbot.handlers.medication.refill_flow import (
    handle_refill_text,
    select_refill_medication,
    start_refill_medication,
)


async def cancel_medication_flow(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Cancel medication-related flows."""
    query = update.callback_query
    await query.answer()

    context.user_data.pop("add_medication", None)
    context.user_data.pop("refill_medication", None)

    await show_medications_screen(update)


async def handle_medication_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Route medication callbacks."""
    query = update.callback_query

    if query.data == "menu_medications":
        await show_medications_screen(update)
        return True

    if query.data == "med_add":
        await start_add_medication(update, context)
        return True

    if query.data == "med_refill":
        await start_refill_medication(update, context)
        return True

    if query.data == "med_cancel":
        await cancel_medication_flow(update, context)
        return True

    if query.data.startswith("med_refill_select_"):
        medication_id = query.data.replace("med_refill_select_", "")
        await select_refill_medication(update, context, medication_id)
        return True

    if query.data.startswith("med_view_"):
        medication_id = query.data.replace("med_view_", "")
        await query.answer()
        await query.edit_message_text(
            f"Medication detail screen coming next for medication ID: {medication_id}"
        )
        return True

    return False


async def handle_medication_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Route medication text flows."""
    if await handle_refill_text(update, context):
        return True

    if await handle_add_medication_text(update, context):
        return True

    return False