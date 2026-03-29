# app.py
from flask import Flask, render_template, redirect, request
from database import init_db, get_connection

app = Flask(__name__)

# --- Atena: base route ---
@app.route("/")
def index():
    return render_template("base.html")

# --- Hamed: add burndown + sprint proposal routes in his branch ---

# --- Homa: add sprint lock + status change routes in her branch ---
@app.route("/sprint")
def sprint():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sprint")
    sprints = c.fetchall()
    c.execute("SELECT * FROM pbi WHERE sprint_id IS NOT NULL")
    sprint_pbis = c.fetchall()
    conn.close()
    return render_template("sprint.html", sprints=sprints, sprint_pbis=sprint_pbis)

@app.route("/sprint/<int:sprint_id>/status", methods=["POST"])
def update_sprint_status(sprint_id):
    conn = get_connection()
    c = conn.cursor()

    # Get current status of this sprint
    c.execute("SELECT status FROM sprint WHERE id = ?", (sprint_id,))
    sprint = c.fetchone()

    # Move to next status
    if sprint[0] == "Planned":
        new_status = "Active"
    elif sprint[0] == "Active":
        new_status = "Complete"
    else:
        new_status = sprint[0]  # already Complete, don't change

    # Save the new status
    c.execute("UPDATE sprint SET status = ? WHERE id = ?", (new_status, sprint_id))
    conn.commit()

    # If sprint just became Complete, return unfinished PBIs to backlog
    if new_status == "Complete":
        return_unfinished_pbis(c, sprint_id)
        conn.commit()

    conn.close()
    return redirect("/sprint")

def return_unfinished_pbis(c, sprint_id):
    # Find all PBIs in this sprint that are not complete
    c.execute("""
        SELECT id, effort FROM pbi
        WHERE sprint_id = ? AND status != 'Complete'
    """, (sprint_id,))
    unfinished = c.fetchall()

    for pbi in unfinished:
        pbi_id = pbi[0]
        original_effort = pbi[1]

        # Get how much effort was already logged for this PBI's tasks
        c.execute("""
            SELECT COALESCE(SUM(actual_effort), 0)
            FROM effort_log
            WHERE task_id IN (
                SELECT id FROM task WHERE pbi_id = ?
            )
        """, (pbi_id,))
        completed_effort = c.fetchone()[0]

        # Remaining effort = original estimate minus what was completed
        remaining_effort = max(0, original_effort - completed_effort)

        # Move PBI back to backlog — clear sprint, update effort estimate
        c.execute("""
            UPDATE pbi
            SET sprint_id = NULL,
                status = 'Incomplete',
                effort = ?
            WHERE id = ?
        """, (remaining_effort, pbi_id))
# --- Setayesh: add login + approval + task status routes in her branch ---

# --- Sasan: add client view routes in his branch ---

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
