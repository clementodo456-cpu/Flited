from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ Add Task", callback_data="btn_add_task")],
        [InlineKeyboardButton("📋 My Tasks", callback_data="btn_tasks"), InlineKeyboardButton("📅 Today", callback_data="btn_today")],
        [InlineKeyboardButton("⏰ Upcoming", callback_data="btn_upcoming"), InlineKeyboardButton("✅ Completed", callback_data="btn_completed")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="btn_settings"), InlineKeyboardButton("❓ Help", callback_data="btn_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard():
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="btn_main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard():
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]]
    return InlineKeyboardMarkup(keyboard)

def priority_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔴 High", callback_data="prio_🔴 High"),
            InlineKeyboardButton("🟡 Medium", callback_data="prio_🟡 Medium"),
            InlineKeyboardButton("🟢 Low", callback_data="prio_🟢 Low")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def category_keyboard(categories: list[str]):
    keyboard = []
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("➕ Custom Category", callback_data="cat_CUSTOM")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")])
    return InlineKeyboardMarkup(keyboard)

def recurrence_keyboard():
    keyboard = [
        [InlineKeyboardButton("None", callback_data="rec_None")],
        [InlineKeyboardButton("📅 Daily", callback_data="rec_Daily"), InlineKeyboardButton("📆 Weekly", callback_data="rec_Weekly")],
        [InlineKeyboardButton("🗓 Monthly", callback_data="rec_Monthly")],
        [InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def task_action_keyboard(task_id: int, status: str = "pending"):
    if status == "pending":
        keyboard = [
            [InlineKeyboardButton("✅ Complete", callback_data=f"act_complete_{task_id}"), InlineKeyboardButton("✏️ Edit", callback_data=f"act_edit_{task_id}")],
            [InlineKeyboardButton("🗑 Delete", callback_data=f"act_delete_{task_id}")],
            [InlineKeyboardButton("⬅️ Back to Tasks", callback_data="btn_tasks")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔄 Restore", callback_data=f"act_restore_{task_id}"), InlineKeyboardButton("🗑 Delete Permanently", callback_data=f"act_pdelete_{task_id}")],
            [InlineKeyboardButton("⬅️ Back to Completed", callback_data="btn_completed")]
        ]
    return InlineKeyboardMarkup(keyboard)

def task_edit_keyboard(task_id: int):
    keyboard = [
        [InlineKeyboardButton("Title", callback_data=f"edf_title_{task_id}"), InlineKeyboardButton("Description", callback_data=f"edf_desc_{task_id}")],
        [InlineKeyboardButton("Due Date", callback_data=f"edf_date_{task_id}"), InlineKeyboardButton("Due Time", callback_data=f"edf_time_{task_id}")],
        [InlineKeyboardButton("Priority", callback_data=f"edf_prio_{task_id}"), InlineKeyboardButton("Category", callback_data=f"edf_cat_{task_id}")],
        [InlineKeyboardButton("Recurrence", callback_data=f"edf_rec_{task_id}")],
        [InlineKeyboardButton("⬅️ Back to Task", callback_data=f"act_view_{task_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)
