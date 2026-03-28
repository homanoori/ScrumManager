# app.py
import os
from datetime import datetime, timedelta

# matplotlib must be set to a non-GUI backend BEFORE pyplot is imported.
# 'Agg' renders to a PNG file without opening a window — required on servers.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for

from database import (
    init_db,
    # PBI
    get_all_pbis, get_unassigned_pbis, add_pbi,
    # Sprint
    get_all_sprints, get_sprint, create_sprint, assign_pbis_to_sprint,
    # Task
    get_all_tasks, add_task,
    # Effort log
    log_effort,
    get_daily_effort_for_sprint, get_sprint_total_effort, get_velocity_data,
)

app = Flask(__name__)


# ===========================================================================
# SP-02 — Sprint Proposal Algorithm
# ===========================================================================

def propose_sprint(capacity):
    """
    Propose a set of PBIs for a new sprint given a capacity limit.

    Algorithm
    ---------
    1. Fetch all Incomplete PBIs that have not been assigned to a sprint yet.
    2. Sort by priority (H before M before L).
       Ties in priority are broken by effort ascending (smallest item first).
    3. Greedily add items while remaining capacity allows — never exceed it.

    Edge cases handled
    ------------------
    - Empty backlog           → returns ([], helpful message)
    - Nothing fits            → returns ([], message with smallest-item hint)
    - Items with equal prio   → sorted by effort so smallest goes in first,
                                which maximises the chance of fitting more items

    Returns
    -------
    (list[dict], None)      — proposed items, no error
    ([], str)               — empty list, human-readable error message
    """
    rows = get_unassigned_pbis()

    if not rows:
        return [], "The backlog has no incomplete, unassigned items to propose for a sprint."

    # Convert DB tuples → plain dicts for readability
    pbis = [
        {"id": r[0], "title": r[1], "priority": r[2], "effort": r[3]}
        for r in rows
    ]

    # Numeric rank lets Python's sort() handle priority correctly.
    # Unknown priority letters fall to rank 9 (end of list) for safety.
    priority_rank = {"H": 0, "M": 1, "L": 2}
    pbis.sort(key=lambda p: (priority_rank.get(p["priority"], 9), p["effort"]))

    # Greedy packing — iterate sorted list, add item only if it fits
    selected = []
    remaining = capacity
    for pbi in pbis:
        if pbi["effort"] <= remaining:
            selected.append(pbi)
            remaining -= pbi["effort"]

    if not selected:
        smallest = min(p["effort"] for p in pbis)
        return [], (
            f"No items fit within a capacity of {capacity}. "
            f"The smallest available item requires {smallest} effort points. "
            f"Try increasing the sprint capacity."
        )

    return selected, None


# ===========================================================================
# SP-07 — Burndown Chart Generator
# ===========================================================================

def generate_burndown_chart(sprint_id, total_effort, daily_logs, duration_days, start_date_str):
    """
    Generate and save a burndown chart PNG for the given sprint.

    The chart shows two lines:
    - Ideal  (blue dashed): straight line from total_effort on day 0 to 0 on the last day
    - Actual (red solid) : starts at total_effort; drops each day effort is logged

    Parameters
    ----------
    sprint_id      : int
    total_effort   : float  — sum of effort of all tasks in the sprint
    daily_logs     : list of (date_str, effort) — one row per day with logged effort
    duration_days  : int    — sprint length (used for ideal line)
    start_date_str : str|None — 'YYYY-MM-DD'; if None, inferred from first log entry

    Returns
    -------
    str   — path relative to /static/, e.g. 'charts/burndown_1.png'
    None  — if there is no effort to chart
    """
    if total_effort == 0:
        return None

    # --- Determine sprint start date ---
    if start_date_str:
        sprint_start = datetime.strptime(start_date_str, "%Y-%m-%d")
    elif daily_logs:
        sprint_start = datetime.strptime(daily_logs[0][0], "%Y-%m-%d")
    else:
        # No logs yet — anchor the ideal line to today
        sprint_start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    # --- Ideal line ---
    # Linear from (day 0 → total_effort) to (day duration_days → 0)
    ideal_dates = [sprint_start + timedelta(days=d) for d in range(duration_days + 1)]
    ideal_remaining = [
        total_effort * (1 - d / duration_days) for d in range(duration_days + 1)
    ]

    # --- Actual line ---
    # Starts at total_effort on sprint_start; each logged day subtracts its effort
    actual_dates = [sprint_start]
    actual_remaining = [total_effort]
    cumulative = 0.0
    for date_str, day_effort in daily_logs:
        cumulative += day_effort
        actual_dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        actual_remaining.append(max(0.0, total_effort - cumulative))

    # --- Draw ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ideal_dates, ideal_remaining, "b--", linewidth=2, label="Ideal")
    ax.plot(actual_dates, actual_remaining, "r-o", linewidth=2, markersize=5, label="Actual")
    ax.set_title(f"Burndown Chart — Sprint {sprint_id}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Remaining Effort (hours)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    fig.autofmt_xdate()

    # Save to static/charts/ — Flask serves /static/ automatically
    charts_dir = os.path.join(os.path.dirname(__file__), "static", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    filename = f"burndown_{sprint_id}.png"
    fig.savefig(os.path.join(charts_dir, filename), bbox_inches="tight")
    plt.close(fig)  # Free memory — important in a long-running server

    return f"charts/{filename}"


# ===========================================================================
# Routes
# ===========================================================================

# --- Home ---

@app.route("/")
def index():
    return render_template("base.html")


# --- Backlog ---

@app.route("/backlog")
def backlog():
    pbis = get_all_pbis()
    return render_template("backlog.html", pbis=pbis)


@app.route("/backlog/add", methods=["POST"])
def backlog_add():
    title    = request.form["title"].strip()
    priority = request.form["priority"]
    effort   = request.form["effort"]
    if title and priority in ("H", "M", "L"):
        try:
            add_pbi(title, priority, float(effort))
        except ValueError:
            pass  # Bad effort value — silently skip
    return redirect(url_for("backlog"))


# --- Sprint Backlog (SP-02) ---

@app.route("/sprint")
def sprint():
    sprints = get_all_sprints()
    return render_template("sprint.html", sprints=sprints)


@app.route("/sprint/propose", methods=["POST"])
def sprint_propose():
    """Run the proposal algorithm and show the result on the sprint page."""
    try:
        capacity = float(request.form["capacity"])
        if capacity <= 0:
            raise ValueError
    except (ValueError, KeyError):
        return render_template(
            "sprint.html",
            sprints=get_all_sprints(),
            proposal_error="Please enter a valid positive number for capacity."
        )

    proposed, error = propose_sprint(capacity)
    return render_template(
        "sprint.html",
        sprints=get_all_sprints(),
        proposed=proposed,          # list of dicts — shown in the confirmation form
        proposal_capacity=capacity,
        proposal_error=error,
    )


@app.route("/sprint/create", methods=["POST"])
def sprint_create():
    """Confirm the proposal: create the sprint row and assign PBIs to it."""
    try:
        capacity = float(request.form["capacity"])
    except (ValueError, KeyError):
        return redirect(url_for("sprint"))

    pbi_ids       = [int(x) for x in request.form.getlist("pbi_ids")]
    start_date    = request.form.get("start_date") or None
    duration_days = int(request.form.get("duration_days") or 14)

    if pbi_ids:
        sprint_id = create_sprint(capacity, start_date, duration_days)
        assign_pbis_to_sprint(sprint_id, pbi_ids)

    return redirect(url_for("sprint"))


# --- Tasks ---

@app.route("/tasks")
def tasks():
    all_tasks = get_all_tasks()
    all_pbis  = get_all_pbis()
    return render_template("tasks.html", tasks=all_tasks, pbis=all_pbis)


@app.route("/tasks/add", methods=["POST"])
def tasks_add():
    title  = request.form["title"].strip()
    effort = request.form["effort"]
    pbi_id = request.form["pbi_id"]
    if title:
        try:
            add_task(title, float(effort), int(pbi_id))
        except (ValueError, KeyError):
            pass
    return redirect(url_for("tasks"))


@app.route("/log_effort", methods=["POST"])
def log_effort_route():
    """Log actual effort spent on a task for a specific date."""
    try:
        task_id       = int(request.form["task_id"])
        date          = request.form["date"]
        actual_effort = float(request.form["actual_effort"])
        if actual_effort > 0 and date:
            log_effort(task_id, date, actual_effort)
    except (ValueError, KeyError):
        pass
    return redirect(url_for("tasks"))


# --- Reports (SP-07) ---

@app.route("/reports")
def reports():
    sprints  = get_all_sprints()
    velocity = get_velocity_data()
    return render_template("reports.html", sprints=sprints, velocity=velocity)


@app.route("/reports/<int:sprint_id>")
def reports_sprint(sprint_id):
    """Generate the burndown chart for a sprint and display the reports page."""
    sprint_row = get_sprint(sprint_id)
    if sprint_row is None:
        return redirect(url_for("reports"))

    # sprint_row columns: id, capacity, status, start_date, duration_days
    _, capacity, status, start_date, duration_days = sprint_row
    duration_days = duration_days or 14

    total_effort = get_sprint_total_effort(sprint_id)
    daily_logs   = get_daily_effort_for_sprint(sprint_id)
    velocity     = get_velocity_data()
    sprints      = get_all_sprints()

    chart_path = generate_burndown_chart(
        sprint_id, total_effort, daily_logs, duration_days, start_date
    )

    return render_template(
        "reports.html",
        sprints=sprints,
        velocity=velocity,
        selected_sprint_id=sprint_id,
        total_effort=total_effort,
        chart_path=chart_path,
    )


# ===========================================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
