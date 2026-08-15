import pytz
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from services.task_service import get_user_timezone, set_user_timezone
from utils.keyboards import back_to_menu_keyboard, cancel_keyboard

SET_TZ = 1

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tz = get_user_timezone(user_id)
    text = (
        "⚙️ *Settings*\n\n"
        f"🌍 *Current Timezone:* `{tz}`\n\n"
        "To update your timezone, type a valid timezone identifier (e.g., `Europe/London`, `America/New_York`, `Asia/Tokyo`, `UTC`, `Africa/Lagos`)."
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    return SET_TZ

async def save_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz_input = update.message.text.strip()
    if tz_input in pytz.all_timezones:
        set_user_timezone(update.effective_user.id, tz_input)
        await update.message.reply_text(f"✅ Timezone updated to *{tz_input}*!", parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Invalid timezone identifier. Please try again (e.g., `UTC`, `America/New_York`):", parse_mode="Markdown", reply_markup=cancel_keyboard())
        return SET_TZ

async def cancel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action canceled.", reply_markup=back_to_menu_keyboard())
    return ConversationHandler.END

settings_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("settings", settings_command)],
    states={
        SET_TZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_timezone)]
    },
    fallbacks=[CommandHandler("cancel", cancel_settings)]
)
