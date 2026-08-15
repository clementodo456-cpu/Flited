from datetime import datetime
import pytz
from telegram.ext import ContextTypes
from database import get_connection
from utils.dates import format_display_datetime

async def check_reminders_job(context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query pending tasks
    cursor.execute("SELECT * FROM tasks WHERE status = 'pending' AND due_date IS NOT NULL AND due_time IS NOT NULL")
    tasks = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    for task in tasks:
        try:
            user_id = task["user_id"]
            # Fetch user timezone
            conn_u = get_connection()
            cursor_u = conn_u.cursor()
            cursor_u.execute("SELECT timezone FROM users WHERE user_id = ?", (user_id,))
            row = cursor_u.fetchone()
            conn_u.close()
            
            tz_str = row["timezone"] if row and row["timezone"] else "UTC"
            user_tz = pytz.timezone(tz_str)
            now_user = datetime.now(user_tz)
            
            # Target datetime string format: YYYY-MM-DD HH:MM
            now_formatted = now_user.strftime("%Y-%m-%d %H:%M")
            task_formatted = f"{task['due_date']} {task['due_time']}"
            
            if now_formatted == task_formatted:
                text = (
                    f"⏰ *Task Reminder*\n\n"
                    f"📌 *{task['title']}*\n"
                    f"📅 {format_display_datetime(task['due_date'], task['due_time'])}\n"
                    f"🏷 Category: {task['category']}\n"
                    f"Priority: {task['priority']}"
                )
                await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Error executing reminder job for task {task['id']}: {e}")
