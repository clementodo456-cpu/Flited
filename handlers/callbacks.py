from telegram import Update
from telegram.ext import ContextTypes
from services.task_service import (
    get_task, complete_task, restore_task, delete_task, update_task_field
)
from utils.dates import format_display_datetime
from utils.keyboards import task_action_keyboard, task_edit_keyboard, back_to_menu_keyboard
from handlers.start import start_command
from handlers.help import help_command
from handlers.settings import settings_command
from handlers.tasks import (
    list_tasks_command, today_command, upcoming_command,
    completed_command, stats_command
)

async def generic_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    # Navigation Actions
    if data == "btn_main_menu":
        await start_command(update, context)
    elif data == "btn_tasks":
        await list_tasks_command(update, context)
    elif data == "btn_today":
        await today_command(update, context)
    elif data == "btn_upcoming":
        await upcoming_command(update, context)
    elif data == "btn_completed":
        await completed_command(update, context)
    elif data == "btn_settings":
        await settings_command(update, context)
    elif data == "btn_help":
        await help_command(update, context)
    elif data == "btn_stats":
        await stats_command(update, context)
        
    # Task View Action
    elif data.startswith("act_view_"):
        task_id = int(data.split("_")[2])
        task = get_task(task_id, user_id)
        if not task:
            await query.message.edit_text("❌ Task not found or unauthorized access.", reply_markup=back_to_menu_keyboard())
            return
            
        dt = format_display_datetime(task["due_date"], task["due_time"])
        text = (
            f"📌 *{task['title']}*\n\n"
            f"📝 *Description:* {task['description'] or 'None'}\n"
            f"📅 *Due:* {dt}\n"
            f"🎯 *Priority:* {task['priority']}\n"
            f"🏷 *Category:* {task['category']}\n"
            f"🔄 *Recurrence:* {task['recurrence']}\n"
            f"Status: *{task['status'].capitalize()}*"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=task_action_keyboard(task_id, task["status"]))

    # Task Management Actions
    elif data.startswith("act_complete_"):
        task_id = int(data.split("_")[2])
        complete_task(task_id, user_id)
        await query.message.edit_text("✅ Task marked as completed!", reply_markup=back_to_menu_keyboard())
        
    elif data.startswith("act_restore_"):
        task_id = int(data.split("_")[2])
        restore_task(task_id, user_id)
        await query.message.edit_text("🔄 Task restored to active list!", reply_markup=back_to_menu_keyboard())

    elif data.startswith("act_delete_") or data.startswith("act_pdelete_"):
        task_id = int(data.split("_")[2])
        delete_task(task_id, user_id)
        await query.message.edit_text("🗑 Task permanently deleted.", reply_markup=back_to_menu_keyboard())

    elif data.startswith("act_edit_"):
        task_id = int(data.split("_")[2])
        await query.message.edit_text("✏️ Choose field to edit:", reply_markup=task_edit_keyboard(task_id))
