import sqlite3

DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT
        )
    """)

    # PBIs
    c.execute("""
        CREATE TABLE IF NOT EXISTS pbi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            status TEXT
        )
    """)

    # Tasks
    c.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            status TEXT,
            pbi_id INTEGER
        )
    """)

    # Approvals
    c.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sprint_id INTEGER,
            approved_at TEXT
        )
    """)

    # Test data
    c.execute("INSERT INTO pbi (title, status) VALUES ('Test PBI', 'Incomplete')")
    c.execute("INSERT INTO task (title, status, pbi_id) VALUES ('Test Task 1', 'To Do', 1)")

    conn.commit()
    conn.close()


def get_or_create_user(username, role):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id FROM user WHERE username = ? AND role = ?", (username, role))
    row = c.fetchone()

    if row:
        user_id = row[0]
    else:
        c.execute("INSERT INTO user (username, role) VALUES (?, ?)", (username, role))
        user_id = c.lastrowid
        conn.commit()

    conn.close()
    return user_id


def add_approval(user_id, sprint_id, approved_at):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "INSERT INTO approvals (user_id, sprint_id, approved_at) VALUES (?, ?, ?)",
        (user_id, sprint_id, approved_at)
    )

    conn.commit()
    conn.close()


def get_all_tasks():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM task")
    rows = c.fetchall()

    conn.close()
    return rows


def get_all_pbis():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM pbi")
    rows = c.fetchall()

    conn.close()
    return rows


def update_task_status(task_id, new_status):
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE task SET status = ? WHERE id = ?", (new_status, task_id))

    conn.commit()
    conn.close()