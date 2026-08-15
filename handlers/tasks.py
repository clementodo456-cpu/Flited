from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from services.task_service import (
    create_task, get_active_tasks, get_task, get_tasks_due_today,
    get_upcoming_tasks, get_completed_tasks, complete_task, restore_task,
    delete_task, update_task_field, get_categories, add_category,
    search_tasks, get_user_stats, get_user_timezone
)
from utils.dates import parse_user_date, parse_user_time, format_display_datetime
from utils.keyboards import (
    main_menu_keyboard, back_to_menu_keyboard, cancel_keyboard,
    priority_keyboard, category_keyboard, recurrence_keyboard,
    task_action_keyboard, task_edit_keyboard
)

# Conversation States for Adding Task
TITLE, DESC, DATE, TIME, PRIORITY, CATEGORY, CUSTOM_CAT, RECURRENCE = range(8)

# Conversation States for Editing Task
EDIT_VALUE = 8

# ADD TASK FLOW
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_task"] = {}
    text = "➕ *Create New Task*\n\nPlease enter the *task title*:"
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cancel_keyboard())
    return TITLE

async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text.strip()
    if not title:
        await update.message.reply_text("❌ Title cannot be empty. Enter task title:")
        return TITLE
    context.user_data["new_task"]["title"] = title
    
    await update.message.reply_text(
        "📝 Enter a *description* (or send /skip to omit):",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    return DESC

async def add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_task"]["description"] = update.message.text.strip()
    await ask_due_date(update, context)
    return DATE

async def add_desc_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_task"]["description"] = ""
    await ask_due_date(update, context)
    return DATE

async def ask_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Enter *due date* (e.g., `today`, `tomorrow`, `20 Aug 2026`, `25/08/2026`, or /skip):",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

async def add_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz = get_user_timezone(update.effective_user.id)
    parsed = parse_user_date(update.message.text, tz)
    if not parsed:
        await update.message.reply_text("❌ Invalid date format. Try `today`, `tomorrow`, or `YYYY-MM-DD`:")
        return DATE
    context.user_data["new_task"]["due_date"] = parsed
    await ask_due_time(update, context)
    return TIME

async def add_date_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_task"]["due_date"] = None
    context.user_data["new_task"]["due_time"] = None
    await ask_priority(update, context)
    return PRIORITY

async def ask_due_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏰ Enter *due time* (e.g., `18:00`, `6:00 PM`, or /skip):",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

async def add_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parsed = parse_user_time(update.message.text)
    if not parsed:
        await update.message.reply_text("❌ Invalid time format. Try `18:00` or `6 PM`:")
        return TIME
    context.user_data["new_task"]["due_time"] = parsed
    await ask_priority(update, context)
    return PRIORITY

async def add_time_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_task"]["due_time"] = None
    await ask_priority(update, context)
    return PRIORITY

async def ask_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Choose task *priority*:",
        parse_mode="Markdown",
        reply_markup=priority_keyboard()
    )

async def add_priority_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prio = query.data.replace("prio_", "")
    context.user_data["new_task"]["priority"] = prio
    
    cats = get_categories(query.from_user.id)
    await query.message.edit_text("🏷 Select a *category*:", parse_mode="Markdown", reply_markup=category_keyboard(cats))
    return CATEGORY

async def add_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    
    if cat == "CUSTOM":
        await query.message.edit_text("🏷 Enter custom category name:", reply_markup=cancel_keyboard())
        return CUSTOM_CAT
        
    context.user_data["new_task"]["category"] = cat
    await query.message.edit_text("🔄 Select *recurrence* pattern:", parse_mode="Markdown", reply_markup=recurrence_keyboard())
    return RECURRENCE

async def add_custom_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text.strip()
    user_id = update.effective_user.id
    add_category(user_id, cat)
    context.user_data["new_task"]["category"] = cat
    await update.message.reply_text("🔄 Select *recurrence* pattern:", parse_mode="Markdown", reply_markup=recurrence_keyboard())
    return RECURRENCE

async def add_recurrence_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rec = query.data.replace("rec_", "")
    context.user_data["new_task"]["recurrence"] = rec
    
    user_id = query.from_user.id
    task_id = create_task(user_id, context.user_data["new_task"])
    
    t = context.user_data["new_task"]
    summary = (
        f"✅ *Task Created Successfully!*\n\n"
        f"📌 *{t['title']}*\n"
        f"📝 {t.get('description') or 'No description'}\n"
        f"📅 {format_display_datetime(t.get('due_date'), t.get('due_time'))}\n"
        f"🎯 Priority: {t.get('priority')}\n"
        f"🏷 Category: {t.get('category')}\n"
        f"🔄 Recurrence: {t.get('recurrence')}"
    )
    await query.message.edit_text(summary, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
    return ConversationHandler.END

async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.edit_text("❌ Task creation canceled.", reply_markup=back_to_menu_keyboard())
    else:
        await update.message.reply_text("❌ Task creation canceled.", reply_markup=back_to_menu_keyboard())
    return ConversationHandler.END

# LISTING & DISPLAY COMMANDS
async def list_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_active_tasks(user_id)
    
    if not tasks:
        msg = "📋 You have no active tasks."
        kb = back_to_menu_keyboard()
    else:
        msg = f"📋 *Active Tasks ({len(tasks)}):*\n\n"
        kb_builder = []
        for task in tasks:
            dt = format_display_datetime(task['due_date'], task['due_time'])
            msg += f"• *{task['title']}* | {task['priority']} | 📅 {dt}\n"
            kb_builder.append([InlineKeyboardButton(f"📌 {task['title']}", callback_data=f"act_view_{task['id']}")])
        kb_builder.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="btn_main_menu")])
        kb = InlineKeyboardMarkup(kb_builder)
        
    if update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tz = get_user_timezone(user_id)
    today_str = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d")
    tasks = get_tasks_due_today(user_id, today_str)
    
    if not tasks:
        msg = "📅 No tasks scheduled for today!"
        kb = back_to_menu_keyboard()
    else:
        msg = "📅 *Tasks Due Today:*\n\n"
        kb_builder = []
        for t in tasks:
            time_str = f" at {t['due_time']}" if t['due_time'] else ""
            msg += f"{t['priority']} *{t['title']}*{time_str} ({t['category']})\n"
            kb_builder.append([InlineKeyboardButton(f"📌 {t['title']}", callback_data=f"act_view_{t['id']}")])
        kb_builder.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="btn_main_menu")])
        kb = InlineKeyboardMarkup(kb_builder)

    if update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

async def upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tz = get_user_timezone(user_id)
    today_str = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d")
    tasks = get_upcoming_tasks(user_id, today_str)
    
    if not tasks:
        msg = "⏰ No upcoming tasks found."
        kb = back_to_menu_keyboard()
    else:
        msg = "⏰ *Upcoming Tasks:*\n\n"
        kb_builder = []
        for t in tasks:
            msg += f"📅 {t['due_date']} - *{t['title']}* ({t['priority']})\n"
            kb_builder.append([InlineKeyboardButton(f"📌 {t['title']}", callback_data=f"act_view_{t['id']}")])
        kb_builder.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="btn_main_menu")])
        kb = InlineKeyboardMarkup(kb_builder)

    if update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

async def completed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_completed_tasks(user_id)
    
    if not tasks:
        msg = "✅ No completed tasks."
        kb = back_to_menu_keyboard()
    else:
        msg = "✅ *Completed Tasks:*\n\n"
        kb_builder = []
        for t in tasks:
            msg += f"✓ *{t['title']}* (Done: {t['completed_at'][:10] if t['completed_at'] else 'N/A'})\n"
            kb_builder.append([InlineKeyboardButton(f"📌 {t['title']}", callback_data=f"act_view_{t['id']}")])
        kb_builder.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="btn_main_menu")])
        kb = InlineKeyboardMarkup(kb_builder)

    if update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔎 Usage: `/search <keyword>`", parse_mode="Markdown")
        return
    
    query = " ".join(context.args)
    user_id = update.effective_user.id
    tasks = search_tasks(user_id, query)
    
    if not tasks:
        await update.message.reply_text(f"🔍 No tasks found matching *'{query}'*.", parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
    else:
        msg = f"🔍 *Search Results for '{query}':*\n\n"
        kb_builder = []
        for t in tasks:
            status = "✅" if t['status'] == 'completed' else "⏳"
            msg += f"{status} *{t['title']}* | {t['category']} | {t['priority']}\n"
            kb_builder.append([InlineKeyboardButton(f"📌 {t['title']}", callback_data=f"act_view_{t['id']}")])
        kb_builder.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="btn_main_menu")])
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb_builder))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tz = get_user_timezone(user_id)
    today_str = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d")
    s = get_user_stats(user_id, today_str)
    
    text = (
        "📊 *Your Productivity Statistics*\n\n"
        f"📂 *Total Tasks:* `{s['total']}`\n"
        f"⏳ *Pending Tasks:* `{s['pending']}`\n"
        f"✅ *Completed Tasks:* `{s['completed']}`\n"
        f"⚠️ *Overdue Tasks:* `{s['overdue']}`\n"
        f"📈 *Completion Rate:* `{s['percentage']}%`"
    )
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())

# ADD TASK CONVERSATION HANDLER
add_task_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_start),
        CallbackQueryHandler(add_start, pattern="^btn_add_task$")
    ],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_title)],
        DESC: [
            CommandHandler("skip", add_desc_skip),
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_desc)
        ],
        DATE: [
            CommandHandler("skip", add_date_skip),
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_date)
        ],
        TIME: [
            CommandHandler("skip", add_time_skip),
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_time)
        ],
        PRIORITY: [CallbackQueryHandler(add_priority_callback, pattern="^prio_")],
        CATEGORY: [CallbackQueryHandler(add_category_callback, pattern="^cat_")],
        CUSTOM_CAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_custom_category)],
        RECURRENCE: [CallbackQueryHandler(add_recurrence_callback, pattern="^rec_")]
    },
    fallbacks=[
        CommandHandler("cancel", cancel_add),
        CallbackQueryHandler(cancel_add, pattern="^btn_cancel$")
    ]
)
