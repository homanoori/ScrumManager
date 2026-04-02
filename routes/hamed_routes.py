import os
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Blueprint, render_template, redirect, request, url_for
from database import (
    get_all_pbis, get_unassigned_pbis, add_pbi,
    get_all_sprints, get_sprint, create_sprint, assign_pbis_to_sprint,
    get_all_tasks, add_task,
    log_effort,
    get_daily_effort_for_sprint, get_sprint_total_effort, get_velocity_data,
)

hamed_bp = Blueprint("hamed", __name__)


def propose_sprint(capacity):
    rows = get_unassigned_pbis()
    if not rows:
        return [], "The backlog has no incomplete, unassigned items to propose for a sprint."
    pbis = [
        {"id": r[0], "title": r[1], "priority": r[2], "effort": r[3]}
        for r in rows
    ]
    priority_rank = {"H": 0, "M": 1, "L": 2}
    pbis.sort(key=lambda p: (priority_rank.get(p["priority"], 9), p["effort"]))
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


def generate_burndown_chart(sprint_id, total_effort, daily_logs, duration_days, start_date_str):
    if total_effort == 0:
        return None
    if start_date_str:
        sprint_start = datetime.strptime(start_date_str, "%Y-%m-%d")
    elif daily_logs:
        sprint_start = datetime.strptime(daily_logs[0][0], "%Y-%m-%d")
    else:
        sprint_start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    ideal_dates = [sprint_start + timedelta(days=d) for d in range(duration_days + 1)]
    ideal_remaining = [
        total_effort * (1 - d / duration_days) for d in range(duration_days + 1)
    ]
    actual_dates = [sprint_start]
    actual_remaining = [total_effort]
    cumulative = 0.0
    for date_str, day_effort in daily_logs:
        cumulative += day_effort
        actual_dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        actual_remaining.append(max(0.0, total_effort - cumulative))
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
    charts_dir = os.path.join(os.path.dirname(__file__), "..", "static", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    filename = f"burndown_{sprint_id}.png"
    fig.savefig(os.path.join(charts_dir, filename), bbox_inches="tight")
    plt.close(fig)
    return f"charts/{filename}"


@hamed_bp.route("/sprint/propose", methods=["POST"])
def sprint_propose():
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
        proposed=proposed,
        proposal_capacity=capacity,
        proposal_error=error,
    )


@hamed_bp.route("/sprint/create", methods=["POST"])
def sprint_create():
    try:
        capacity = float(request.form["capacity"])
    except (ValueError, KeyError):
        return redirect(url_for("homa.sprint"))
    pbi_ids       = [int(x) for x in request.form.getlist("pbi_ids")]
    start_date    = request.form.get("start_date") or None
    duration_days = int(request.form.get("duration_days") or 14)
    if pbi_ids:
        sprint_id = create_sprint(capacity, start_date, duration_days)
        assign_pbis_to_sprint(sprint_id, pbi_ids)
    return redirect(url_for("homa.sprint"))


@hamed_bp.route("/tasks")
def tasks():
    all_tasks = get_all_tasks()
    all_pbis  = get_all_pbis()
    return render_template("tasks.html", tasks=all_tasks, pbis=all_pbis)


@hamed_bp.route("/tasks/add", methods=["POST"])
def tasks_add():
    title  = request.form["title"].strip()
    effort = request.form["effort"]
    pbi_id = request.form["pbi_id"]
    if title:
        try:
            add_task(title, float(effort), int(pbi_id))
        except (ValueError, KeyError):
            pass
    return redirect(url_for("hamed.tasks"))


@hamed_bp.route("/log_effort", methods=["POST"])
def log_effort_route():
    try:
        task_id       = int(request.form["task_id"])
        date          = request.form["date"]
        actual_effort = float(request.form["actual_effort"])
        if actual_effort > 0 and date:
            log_effort(task_id, date, actual_effort)
    except (ValueError, KeyError):
        pass
    return redirect(url_for("hamed.tasks"))


@hamed_bp.route("/reports")
def reports():
    sprints  = get_all_sprints()
    velocity = get_velocity_data()
    return render_template("reports.html", sprints=sprints, velocity=velocity)


@hamed_bp.route("/reports/<int:sprint_id>")
def reports_sprint(sprint_id):
    sprint_row = get_sprint(sprint_id)
    if sprint_row is None:
        return redirect(url_for("hamed.reports"))
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