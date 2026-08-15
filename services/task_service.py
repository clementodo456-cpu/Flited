from datetime import datetime
import pytz
from database import get_connection

def register_user(user_id: int, username: str, default_tz: str = "UTC"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, timezone) VALUES (?, ?, ?)", (user_id, username, default_tz))
    
    # Default Categories
    defaults = ["Work", "Personal", "Study", "Shopping"]
    for cat in defaults:
        cursor.execute("INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)", (user_id, cat))
        
    conn.commit()
    conn.close()

def get_user_timezone(user_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timezone FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["timezone"] if row and row["timezone"] else "UTC"

def set_user_timezone(user_id: int, tz_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (tz_name, user_id))
    conn.commit()
    conn.close()

def get_categories(user_id: int) -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r["name"] for r in rows]

def add_category(user_id: int, name: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def create_task(user_id: int, data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO tasks (user_id, title, description, due_date, due_time, priority, category, recurrence, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data.get("title"),
        data.get("description", ""),
        data.get("due_date"),
        data.get("due_time"),
        data.get("priority", "🟡 Medium"),
        data.get("category", "General"),
        data.get("recurrence", "None"),
        now_str
    ))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_task(task_id: int, user_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_active_tasks(user_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC, due_time ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tasks_due_today(user_id: int, date_str: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'pending' AND due_date = ? ORDER BY priority ASC", (user_id, date_str))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_upcoming_tasks(user_id: int, today_str: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'pending' AND due_date > ? ORDER BY due_date ASC", (user_id, today_str))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_completed_tasks(user_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'completed' ORDER BY completed_at DESC LIMIT 20", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_tasks(user_id: int, query: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{query}%"
    cursor.execute("""
    SELECT * FROM tasks 
    WHERE user_id = ? AND (title LIKE ? OR description LIKE ? OR category LIKE ?)
    ORDER BY status ASC, due_date ASC
    """, (user_id, q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def complete_task(task_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ? AND user_id = ?", (now_str, task_id, user_id))
    conn.commit()
    conn.close()

def restore_task(task_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'pending', completed_at = NULL WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

def delete_task(task_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

def update_task_field(task_id: int, user_id: int, field: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    allowed_fields = ["title", "description", "due_date", "due_time", "priority", "category", "recurrence"]
    if field in allowed_fields:
        cursor.execute(f"UPDATE tasks SET {field} = ? WHERE id = ? AND user_id = ?", (value, task_id, user_id))
        conn.commit()
    conn.close()

def get_user_stats(user_id: int, today_str: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = 'completed'", (user_id,))
    completed = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = 'pending'", (user_id,))
    pending = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = 'pending' AND due_date < ?", (user_id, today_str))
    overdue = cursor.fetchone()["count"]
    
    conn.close()
    
    pct = round((completed / total * 100), 1) if total > 0 else 0.0
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "percentage": pct
    }
