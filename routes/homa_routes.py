from flask import Blueprint, redirect, request
from database import get_connection

homa_bp = Blueprint("homa", __name__)


@homa_bp.route("/sprint")
def sprint():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sprint")
    sprints = c.fetchall()
    c.execute("SELECT * FROM pbi WHERE sprint_id IS NOT NULL")
    sprint_pbis = c.fetchall()
    conn.close()
    from flask import render_template
    return render_template("sprint.html", sprints=sprints, sprint_pbis=sprint_pbis)


@homa_bp.route("/sprint/<int:sprint_id>/status", methods=["POST"])
def update_sprint_status(sprint_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM sprint WHERE id = ?", (sprint_id,))
    sprint = c.fetchone()
    if sprint[0] == "Planned":
        new_status = "Active"
    elif sprint[0] == "Active":
        new_status = "Complete"
    else:
        new_status = sprint[0]
    c.execute("UPDATE sprint SET status = ? WHERE id = ?", (new_status, sprint_id))
    conn.commit()
    if new_status == "Complete":
        return_unfinished_pbis(c, sprint_id)
        conn.commit()
    conn.close()
    return redirect("/sprint")


def return_unfinished_pbis(c, sprint_id):
    c.execute("""
        SELECT id, effort FROM pbi
        WHERE sprint_id = ? AND status != 'Complete'
    """, (sprint_id,))
    unfinished = c.fetchall()
    for pbi in unfinished:
        pbi_id = pbi[0]
        original_effort = pbi[1]
        c.execute("""
            SELECT COALESCE(SUM(actual_effort), 0)
            FROM effort_log
            WHERE task_id IN (
                SELECT id FROM task WHERE pbi_id = ?
            )
        """, (pbi_id,))
        completed_effort = c.fetchone()[0]
        remaining_effort = max(0, original_effort - completed_effort)
        c.execute("""
            UPDATE pbi
            SET sprint_id = NULL,
                status = 'Incomplete',
                effort = ?
            WHERE id = ?
        """, (remaining_effort, pbi_id))