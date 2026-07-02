"""
caregiver_handler.py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from medbot.caregiver_manager import (
    add_caregiver,
    get_caregiver,
    list_active_caregivers,
    remove_caregiver,
)
from medbot.menu_manager import main_menu_keyboard


def caregiver_keyboard(owner_id: str | None = None) -> InlineKeyboardMarkup:
    rows = []

    if owner_id:
        for caregiver in list_active_caregivers(owner_id):
            rows.append(
                [InlineKeyboardButton(
                    f"👥 {caregiver['name']}",
                    callback_data=f"caregiver_view_{caregiver['caregiver_id']}",
                )]
            )

    rows.append([InlineKeyboardButton("➕ Add Caregiver", callback_data="caregiver_add")])
    rows.append([InlineKeyboardButton("🏠 Home", callback_data="menu_home")])
    return InlineKeyboardMarkup(rows)


def caregiver_detail_keyboard(caregiver_id: str, connected: bool) -> InlineKeyboardMarkup:
    rows = []

    if connected:
        rows.append([InlineKeyboardButton("📨 Send Test Notification", callback_data=f"caregiver_test_{caregiver_id}")])

    rows.extend(
        [
            [InlineKeyboardButton("❌ Remove Caregiver", callback_data=f"caregiver_delete_{caregiver_id}")],
            [InlineKeyboardButton("⬅️ My Caregivers", callback_data="menu_caregivers")],
            [InlineKeyboardButton("🏠 Home", callback_data="menu_home")],
        ]
    )

    return InlineKeyboardMarkup(rows)


def caregiver_delete_keyboard(caregiver_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❌ Yes, remove caregiver", callback_data=f"caregiver_delete_confirm_{caregiver_id}")],
            [InlineKeyboardButton("⬅️ Cancel", callback_data=f"caregiver_view_{caregiver_id}")],
            [InlineKeyboardButton("🏠 Home", callback_data="menu_home")],
        ]
    )


def build_caregiver_screen(owner_id: str) -> str:
    caregivers = list_active_caregivers(owner_id)

    if not caregivers:
        return (
            "👥 My Caregivers\n\n"
            "You have not added any caregivers yet.\n\n"
            "A caregiver can be notified if you do not confirm a medication reminder."
        )

    return (
        "👥 My Caregivers\n\n"
        f"You currently have {len(caregivers)} active caregiver(s).\n\n"
        "Tap a caregiver to view details."
    )


def build_caregiver_detail_screen(caregiver_id: str) -> str:
    caregiver = get_caregiver(caregiver_id)

    if caregiver is None:
        return "I couldn't find that caregiver."

    connected = bool(caregiver.get("telegram_chat_id", ""))
    connection = "🟢 Connected" if connected else "🟡 Waiting for caregiver to start MediBot"

    return (
        "👥 Caregiver Details\n\n"
        f"Name\n{caregiver['name']}\n\n"
        f"Telegram\n{caregiver.get('telegram_username', '')}\n\n"
        f"Connection\n{connection}\n\n"
        "Notifications\n"
        "✅ 30-minute medication alerts\n"
        "✅ 60-minute medication alerts"
    )


async def show_caregiver_screen(update: Update) -> None:
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_caregiver_screen(owner_id),
        reply_markup=caregiver_keyboard(owner_id),
    )


async def show_caregiver_detail(update: Update, caregiver_id: str) -> None:
    query = update.callback_query
    await query.answer()

    caregiver = get_caregiver(caregiver_id)
    connected = bool(caregiver and caregiver.get("telegram_chat_id", ""))

    await query.edit_message_text(
        build_caregiver_detail_screen(caregiver_id),
        reply_markup=caregiver_detail_keyboard(caregiver_id, connected),
    )


async def start_add_caregiver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data["add_caregiver"] = {"step": "name", "data": {}}

    await query.edit_message_text("➕ Add Caregiver\n\nWhat is your caregiver's name?")


async def handle_caregiver_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = context.user_data.get("add_caregiver")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    text = update.message.text.strip()
    step = flow["step"]
    data = flow["data"]

    if step == "name":
        data["name"] = text.title()
        flow["step"] = "telegram_username"

        await update.message.reply_text(
            "Great.\n\n"
            "Please send your caregiver's Telegram username.\n\n"
            "Example:\n@sarahsmith"
        )
        return True

    if step == "telegram_username":
        username = text.strip()

        if not username.startswith("@"):
            await update.message.reply_text(
                "Please enter a Telegram username starting with @.\n\n"
                "Example:\n@sarahsmith"
            )
            return True

        caregiver = add_caregiver(
            owner_id=owner_id,
            name=data["name"],
            telegram_username=username,
        )

        context.user_data.pop("add_caregiver", None)

        await update.message.reply_text(
            "👥 Caregiver Added\n\n"
            f"Name\n{caregiver['name']}\n\n"
            f"Telegram\n{caregiver['telegram_username']}\n\n"
            "Connection\n🟡 Waiting for caregiver to start MediBot\n\n"
            "Once connected, they can receive important medication alerts.",
            reply_markup=main_menu_keyboard(),
        )
        return True

    return False


async def start_delete_caregiver(update: Update, caregiver_id: str) -> None:
    query = update.callback_query
    await query.answer()

    caregiver = get_caregiver(caregiver_id)

    if caregiver is None:
        await query.edit_message_text("I couldn't find that caregiver.")
        return

    await query.edit_message_text(
        "❌ Remove Caregiver\n\n"
        f"{caregiver['name']}\n\n"
        "Are you sure you want to remove this caregiver?\n\n"
        "They will no longer receive medication alerts.",
        reply_markup=caregiver_delete_keyboard(caregiver_id),
    )


async def confirm_delete_caregiver(update: Update, caregiver_id: str) -> None:
    query = update.callback_query
    await query.answer()

    caregiver = get_caregiver(caregiver_id)

    if caregiver is None:
        await query.edit_message_text("I couldn't find that caregiver.")
        return

    remove_caregiver(caregiver_id)
    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        "✅ Caregiver removed.\n\n"
        f"{caregiver['name']} has been removed."
    )

    await query.message.reply_text(
        build_caregiver_screen(owner_id),
        reply_markup=caregiver_keyboard(owner_id),
    )


async def send_test_notification(update: Update, context: ContextTypes.DEFAULT_TYPE, caregiver_id: str) -> None:
    query = update.callback_query
    await query.answer()

    caregiver = get_caregiver(caregiver_id)

    if caregiver is None:
        await query.edit_message_text("I couldn't find that caregiver.")
        return

    chat_id = caregiver.get("telegram_chat_id", "")

    if not chat_id:
        await query.edit_message_text(
            "This caregiver is not connected yet.\n\n"
            "Ask them to start MediBot first.",
            reply_markup=caregiver_detail_keyboard(caregiver_id, False),
        )
        return

    await context.bot.send_message(
        chat_id=int(chat_id),
        text=(
            "👥 MediBot Test Notification\n\n"
            "This is a test notification from MediBot.\n\n"
            "If you received this message, caregiver notifications are working correctly."
        ),
    )

    await query.edit_message_text(
        "✅ Test notification sent.",
        reply_markup=caregiver_detail_keyboard(caregiver_id, True),
    )


async def handle_caregiver_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    query = update.callback_query
    data = query.data

    if data == "menu_caregivers":
        await show_caregiver_screen(update)
        return True

    if data == "caregiver_add":
        await start_add_caregiver(update, context)
        return True

    if data.startswith("caregiver_view_"):
        caregiver_id = data.replace("caregiver_view_", "")
        await show_caregiver_detail(update, caregiver_id)
        return True

    if data.startswith("caregiver_test_"):
        caregiver_id = data.replace("caregiver_test_", "")
        await send_test_notification(update, context, caregiver_id)
        return True

    if data.startswith("caregiver_delete_confirm_"):
        caregiver_id = data.replace("caregiver_delete_confirm_", "")
        await confirm_delete_caregiver(update, caregiver_id)
        return True

    if data.startswith("caregiver_delete_"):
        caregiver_id = data.replace("caregiver_delete_", "")
        await start_delete_caregiver(update, caregiver_id)
        return True

    return False