import sqlite3
from config import DATABASE_URL

def get_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        timezone TEXT DEFAULT 'UTC',
        default_priority TEXT DEFAULT '🟡 Medium'
    )
    """)
    
    # Categories Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        UNIQUE(user_id, name)
    )
    """)
    
    # Tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        due_time TEXT,
        priority TEXT DEFAULT '🟡 Medium',
        category TEXT DEFAULT 'General',
        status TEXT DEFAULT 'pending',
        reminder_time TEXT,
        recurrence TEXT DEFAULT 'None',
        created_at TEXT,
        completed_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()
