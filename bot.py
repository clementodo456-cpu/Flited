import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from database import init_db
from handlers.start import start_command
from handlers.help import help_command
from handlers.settings import settings_conv_handler
from handlers.tasks import (
    add_task_conv_handler, list_tasks_command, today_command,
    upcoming_command, completed_command, search_command, stats_command
)
from handlers.callbacks import generic_callback_handler
from services.reminders import check_reminders_job

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    # Initialize Database Schema
    init_db()
    
    # Initialize Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register Conversation Handlers First
    app.add_handler(add_task_conv_handler)
    app.add_handler(settings_conv_handler)
    
    # Command Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tasks", list_tasks_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("upcoming", upcoming_command))
    app.add_handler(CommandHandler("completed", completed_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Generic Callback Query Handler
    app.add_handler(CallbackQueryHandler(generic_callback_handler))
    
    # Job Queue for Scheduled Reminders (runs every 60 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(check_reminders_job, interval=60, first=10)
    
    logging.info("Starting Telegram Task Manager Bot (@flitedstbot)...")
    app.run_polling()

if __name__ == "__main__":
    main()
