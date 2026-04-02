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
            priority TEXT,
            effort REAL,
            status TEXT DEFAULT 'Incomplete',
            sprint_id INTEGER
        )
    """)

    # Tasks
    c.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            effort REAL,
            status TEXT DEFAULT 'Not Started',
            pbi_id INTEGER,
            FOREIGN KEY (pbi_id) REFERENCES pbi(id)
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
    # Sprint table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sprint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capacity REAL NOT NULL,
            status TEXT DEFAULT 'Planned',
            start_date TEXT,
            duration_days INTEGER DEFAULT 14
        )
    ''')

    # Effort log table
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

    c.execute("SELECT t.id, t.title, t.effort, t.status, t.pbi_id, p.title FROM task t LEFT JOIN pbi p ON t.pbi_id = p.id ORDER BY t.id")
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

def get_unassigned_pbis():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, priority, effort, status "
        "FROM pbi WHERE sprint_id IS NULL AND status = 'Incomplete'"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def add_pbi(title, priority, effort):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO pbi (title, priority, effort) VALUES (?, ?, ?)",
        (title, priority, effort)
    )
    conn.commit()
    conn.close()


def get_all_sprints():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, capacity, status, start_date, duration_days "
        "FROM sprint ORDER BY id"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_sprint(sprint_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, capacity, status, start_date, duration_days "
        "FROM sprint WHERE id = ?",
        (sprint_id,)
    )
    row = c.fetchone()
    conn.close()
    return row


def create_sprint(capacity, start_date=None, duration_days=14):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO sprint (capacity, start_date, duration_days) VALUES (?, ?, ?)",
        (capacity, start_date, duration_days)
    )
    sprint_id = c.lastrowid
    conn.commit()
    conn.close()
    return sprint_id


def assign_pbis_to_sprint(sprint_id, pbi_ids):
    conn = get_connection()
    c = conn.cursor()
    for pbi_id in pbi_ids:
        c.execute(
            "UPDATE pbi SET sprint_id = ? WHERE id = ?",
            (sprint_id, pbi_id)
        )
    conn.commit()
    conn.close()


def add_task(title, effort, pbi_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO task (title, effort, pbi_id) VALUES (?, ?, ?)",
        (title, effort, pbi_id)
    )
    conn.commit()
    conn.close()


def log_effort(task_id, date, actual_effort):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO effort_log (task_id, date, actual_effort) VALUES (?, ?, ?)",
        (task_id, date, actual_effort)
    )
    conn.commit()
    conn.close()


def get_daily_effort_for_sprint(sprint_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT el.date, SUM(el.actual_effort) "
        "FROM effort_log el "
        "JOIN task t ON el.task_id = t.id "
        "JOIN pbi p ON t.pbi_id = p.id "
        "WHERE p.sprint_id = ? "
        "GROUP BY el.date "
        "ORDER BY el.date",
        (sprint_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_sprint_total_effort(sprint_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT COALESCE(SUM(t.effort), 0) "
        "FROM task t JOIN pbi p ON t.pbi_id = p.id "
        "WHERE p.sprint_id = ?",
        (sprint_id,)
    )
    total = c.fetchone()[0]
    conn.close()
    return total


def get_velocity_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT p.sprint_id, COALESCE(SUM(el.actual_effort), 0) "
        "FROM pbi p "
        "LEFT JOIN task t ON t.pbi_id = p.id "
        "LEFT JOIN effort_log el ON el.task_id = t.id "
        "WHERE p.sprint_id IS NOT NULL "
        "GROUP BY p.sprint_id "
        "ORDER BY p.sprint_id"
    )
    rows = c.fetchall()
    conn.close()
    return rows