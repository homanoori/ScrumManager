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
    # start_date and duration_days added by Hamed for burndown chart
    c.execute('''
        CREATE TABLE IF NOT EXISTS sprint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capacity REAL NOT NULL,
            status TEXT DEFAULT 'Planned',
            start_date TEXT,
            duration_days INTEGER DEFAULT 14
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

    # Effort log table — Hamed: log actual effort per task per day for burndown
    c.execute('''
        CREATE TABLE IF NOT EXISTS effort_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            date TEXT,
            actual_effort REAL,
            FOREIGN KEY (task_id) REFERENCES task(id)
        )
    ''')

    # Migrate existing sprint table: add new columns if they don't exist yet.
    # SQLite does not support ALTER TABLE ADD COLUMN IF NOT EXISTS, so we
    # silently ignore the error when the column is already present.
    for migration_sql in [
        "ALTER TABLE sprint ADD COLUMN start_date TEXT",
        "ALTER TABLE sprint ADD COLUMN duration_days INTEGER DEFAULT 14",
    ]:
        try:
            c.execute(migration_sql)
        except Exception:
            pass  # Column already exists — safe to ignore

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# PBI helpers
# ---------------------------------------------------------------------------

def get_all_pbis():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, title, priority, effort, status, sprint_id "
        "FROM pbi ORDER BY id"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_unassigned_pbis():
    """Return Incomplete PBIs that have not been assigned to any sprint yet."""
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


# ---------------------------------------------------------------------------
# Sprint helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task helpers
# ---------------------------------------------------------------------------

def get_all_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT t.id, t.title, t.effort, t.status, t.pbi_id, p.title "
        "FROM task t LEFT JOIN pbi p ON t.pbi_id = p.id "
        "ORDER BY t.id"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def add_task(title, effort, pbi_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO task (title, effort, pbi_id) VALUES (?, ?, ?)",
        (title, effort, pbi_id)
    )
    conn.commit()
    conn.close()


def get_sprint_tasks(sprint_id):
    """All tasks belonging to PBIs assigned to this sprint."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT t.id, t.title, t.effort, t.status, t.pbi_id "
        "FROM task t JOIN pbi p ON t.pbi_id = p.id "
        "WHERE p.sprint_id = ?",
        (sprint_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Effort log helpers (SP-07)
# ---------------------------------------------------------------------------

def log_effort(task_id, date, actual_effort):
    """Record actual effort spent on a task for a specific date."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO effort_log (task_id, date, actual_effort) VALUES (?, ?, ?)",
        (task_id, date, actual_effort)
    )
    conn.commit()
    conn.close()


def get_daily_effort_for_sprint(sprint_id):
    """
    Return (date, total_effort_logged_that_day) for all tasks in the sprint,
    sorted by date ascending.  Used to build the actual burndown line.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT el.date, SUM(el.actual_effort) "
        "FROM effort_log el "
        "JOIN task t ON el.task_id = t.id "
        "JOIN pbi p  ON t.pbi_id  = p.id "
        "WHERE p.sprint_id = ? "
        "GROUP BY el.date "
        "ORDER BY el.date",
        (sprint_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_sprint_total_effort(sprint_id):
    """Sum of effort across ALL tasks belonging to PBIs in this sprint."""
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
    """
    Velocity per sprint = total effort actually logged across all tasks
    in that sprint.  Returns list of (sprint_id, logged_effort).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT p.sprint_id, COALESCE(SUM(el.actual_effort), 0) "
        "FROM pbi p "
        "LEFT JOIN task t        ON t.pbi_id   = p.id "
        "LEFT JOIN effort_log el ON el.task_id = t.id "
        "WHERE p.sprint_id IS NOT NULL "
        "GROUP BY p.sprint_id "
        "ORDER BY p.sprint_id"
    )
    rows = c.fetchall()
    conn.close()
    return rows
