from telegram import Update
from telegram.ext import ContextTypes
from services.task_service import register_user
from utils.keyboards import main_menu_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or user.first_name)
    
    welcome_text = (
        f"👋 Welcome, *{user.first_name}*!\n\n"
        f"I am *@flitedstbot*, your personal task management assistant.\n"
        f"I'll help you organize, schedule, and execute your daily tasks effortlessly.\n\n"
        f"Choose an option below to get started:"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
