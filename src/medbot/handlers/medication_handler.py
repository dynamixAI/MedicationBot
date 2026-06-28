"""
medication_handler.py

Router for medication screens and flows.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from medbot.handlers.medication.add_flow import (
    handle_add_medication_text,
    start_add_medication,
)
from medbot.handlers.medication.delete_flow import (
    confirm_delete_medication,
    start_delete_medication,
)
from medbot.handlers.medication.detail_screen import show_medication_detail_screen
from medbot.handlers.medication.edit_dose_flow import (
    handle_edit_dose_text,
    start_edit_dose,
)
from medbot.handlers.medication.edit_menu import show_edit_medication_menu
from medbot.handlers.medication.edit_name_flow import (
    handle_edit_name_text,
    start_edit_name,
)
from medbot.handlers.medication.edit_stock_flow import (
    handle_edit_stock_text,
    start_edit_stock,
)
from medbot.handlers.medication.edit_strength_flow import (
    handle_edit_strength_text,
    start_edit_strength,
)
from medbot.handlers.medication.edit_times_flow import (
    handle_edit_times_text,
    start_edit_times,
)
from medbot.handlers.medication.history_screen import (
    show_medication_history_screen,
)
from medbot.handlers.medication.list_screen import show_medications_screen
from medbot.handlers.medication.refill_flow import (
    handle_refill_text,
    select_refill_medication,
)


async def safe_answer(update: Update) -> None:
    """Answer callback safely, even if button is old."""
    query = update.callback_query

    try:
        await query.answer()
    except BadRequest:
        pass


def coming_next_keyboard(medication_id: str) -> InlineKeyboardMarkup:
    """Temporary navigation keyboard for unfinished edit actions."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Back to Edit Menu",
                    callback_data=f"med_edit_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back to Medication",
                    callback_data=f"med_view_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="menu_home",
                )
            ],
        ]
    )


async def show_coming_next(
    update: Update,
    medication_id: str,
    message: str,
) -> None:
    """Show temporary coming-next screen with navigation."""
    query = update.callback_query
    await safe_answer(update)

    await query.edit_message_text(
        message,
        reply_markup=coming_next_keyboard(medication_id),
    )


async def cancel_medication_flow(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Cancel medication-related flows."""
    await safe_answer(update)

    context.user_data.pop("add_medication", None)
    context.user_data.pop("refill_medication", None)
    context.user_data.pop("edit_medication_name", None)
    context.user_data.pop("edit_medication_strength", None)
    context.user_data.pop("edit_medication_dose", None)
    context.user_data.pop("edit_medication_times", None)
    context.user_data.pop("edit_medication_stock", None)

    await show_medications_screen(update)


async def handle_medication_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Route medication callbacks."""
    query = update.callback_query
    data = query.data

    if data == "menu_medications":
        await show_medications_screen(update)
        return True

    if data == "med_add":
        await start_add_medication(update, context)
        return True

    if data == "med_cancel":
        await cancel_medication_flow(update, context)
        return True

    if data.startswith("med_view_"):
        medication_id = data.replace("med_view_", "")
        await show_medication_detail_screen(update, medication_id)
        return True

    if data.startswith("med_detail_refill_"):
        medication_id = data.replace("med_detail_refill_", "")
        await select_refill_medication(update, context, medication_id)
        return True

    if data.startswith("med_history_"):
        medication_id = data.replace("med_history_", "")
        await show_medication_history_screen(update, medication_id)
        return True

    if data.startswith("med_delete_confirm_"):
        medication_id = data.replace("med_delete_confirm_", "")
        await confirm_delete_medication(update, context, medication_id)
        return True

    if data.startswith("med_delete_"):
        medication_id = data.replace("med_delete_", "")
        await start_delete_medication(update, context, medication_id)
        return True

    if data.startswith("med_edit_name_"):
        medication_id = data.replace("med_edit_name_", "")
        await start_edit_name(update, context, medication_id)
        return True

    if data.startswith("med_edit_strength_"):
        medication_id = data.replace("med_edit_strength_", "")
        await start_edit_strength(update, context, medication_id)
        return True

    if data.startswith("med_edit_dose_"):
        medication_id = data.replace("med_edit_dose_", "")
        await start_edit_dose(update, context, medication_id)
        return True

    if data.startswith("med_edit_times_"):
        medication_id = data.replace("med_edit_times_", "")
        await start_edit_times(update, context, medication_id)
        return True

    if data.startswith("med_edit_stock_"):
        medication_id = data.replace("med_edit_stock_", "")
        await start_edit_stock(update, context, medication_id)
        return True

    if data.startswith("med_edit_"):
        medication_id = data.replace("med_edit_", "")
        await show_edit_medication_menu(update, medication_id)
        return True

    return False


async def handle_medication_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Route medication text flows."""
    if await handle_edit_name_text(update, context):
        return True

    if await handle_edit_strength_text(update, context):
        return True

    if await handle_edit_dose_text(update, context):
        return True

    if await handle_edit_times_text(update, context):
        return True

    if await handle_edit_stock_text(update, context):
        return True

    if await handle_refill_text(update, context):
        return True

    if await handle_add_medication_text(update, context):
        return True

    return False