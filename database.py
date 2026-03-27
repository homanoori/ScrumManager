# database.py
import sqlite3

def get_connection():
    return sqlite3.connect("sbl.db")

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # PBI table
    c.execute('''
        CREATE TABLE IF NOT EXISTS pbi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            effort REAL NOT NULL,
            status TEXT DEFAULT 'Incomplete',
            sprint_id INTEGER
        )
    ''')

    # Sprint table — Homa adds sprint lock logic here
    c.execute('''
        CREATE TABLE IF NOT EXISTS sprint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capacity REAL NOT NULL,
            status TEXT DEFAULT 'Planned'
        )
    ''')

    # Task table — Setayesh adds task status logic here
    c.execute('''
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            effort REAL NOT NULL,
            status TEXT DEFAULT 'Not Started',
            pbi_id INTEGER,
            FOREIGN KEY (pbi_id) REFERENCES pbi(id)
        )
    ''')

    # User table — Setayesh adds role logic here
    c.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Approvals table — Setayesh adds approval history here
    c.execute('''
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sprint_id INTEGER,
            approved_at TEXT,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (sprint_id) REFERENCES sprint(id)
        )
    ''')

    # Effort log table — Hamed adds burndown logging here
    c.execute('''
        CREATE TABLE IF NOT EXISTS effort_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            date TEXT,
            actual_effort REAL,
            FOREIGN KEY (task_id) REFERENCES task(id)
        )
    ''')

    conn.commit()
    conn.close()
