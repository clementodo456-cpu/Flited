from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import back_to_menu_keyboard

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ *FliteDST Task Bot Help Center*\n\n"
        "*Available Commands:*\n"
        "• `/start` - Start bot & show main menu\n"
        "• `/add` - Create a new task\n"
        "• `/tasks` - Display active tasks\n"
        "• `/today` - Display tasks due today\n"
        "• `/upcoming` - View upcoming schedule\n"
        "• `/completed` - View finished tasks\n"
        "• `/search <keyword>` - Search through tasks\n"
        "• `/stats` - View productivity statistics\n"
        "• `/settings` - Configure timezone & preferences\n"
        "• `/help` - Open this manual\n"
        "• `/cancel` - Abort current operation\n\n"
        "💡 *Tips:* You can use natural date formats like `today`, `tomorrow`, `20 Aug 2026`, or `25/08/2026` when scheduling tasks."
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(help_text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
