import os
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from models import db, PBI, Sprint, Task, EffortLog, AuditLog

hamed_bp = Blueprint("hamed", __name__)


def propose_sprint(capacity):
    pbis = PBI.query.filter_by(sprint_id=None, status="Incomplete").all()
    if not pbis:
        return [], "The backlog has no incomplete, unassigned items to propose for a sprint."
    priority_rank = {"H": 0, "M": 1, "L": 2}
    pbis.sort(key=lambda p: (priority_rank.get(p.priority, 9), p.effort))
    selected = []
    remaining = capacity
    for pbi in pbis:
        if pbi.effort <= remaining:
            selected.append({"id": pbi.id, "title": pbi.title, "priority": pbi.priority, "effort": pbi.effort})
            remaining -= pbi.effort
    if not selected:
        smallest = min(p.effort for p in pbis)
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
        sprint_start = datetime.strptime(str(start_date_str), "%Y-%m-%d")
    elif daily_logs:
        sprint_start = datetime.strptime(str(daily_logs[0][0]), "%Y-%m-%d")
    else:
        sprint_start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    ideal_dates = [sprint_start + timedelta(days=d) for d in range(duration_days + 1)]
    ideal_remaining = [total_effort * (1 - d / duration_days) for d in range(duration_days + 1)]
    actual_dates = [sprint_start]
    actual_remaining = [total_effort]
    cumulative = 0.0
    for date_val, day_effort in daily_logs:
        cumulative += day_effort
        actual_dates.append(datetime.strptime(str(date_val), "%Y-%m-%d"))
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
@login_required
def sprint_propose():
    try:
        capacity = float(request.form["capacity"])
        if capacity <= 0:
            raise ValueError
    except (ValueError, KeyError):
        sprints = Sprint.query.order_by(Sprint.id).all()
        return render_template("sprint.html", sprints=sprints,
                               proposal_error="Please enter a valid positive number for capacity.")
    proposed, error = propose_sprint(capacity)
    sprints = Sprint.query.order_by(Sprint.id).all()
    return render_template("sprint.html", sprints=sprints, proposed=proposed,
                           proposal_capacity=capacity, proposal_error=error)


@hamed_bp.route("/sprint/create", methods=["POST"])
@login_required
def sprint_create():
    try:
        capacity = float(request.form["capacity"])
    except (ValueError, KeyError):
        return redirect(url_for("homa.sprint"))
    pbi_ids = [int(x) for x in request.form.getlist("pbi_ids")]
    if pbi_ids:
        sprint = Sprint(capacity=capacity, status="Planned")
        db.session.add(sprint)
        db.session.flush()
        PBI.query.filter(PBI.id.in_(pbi_ids)).update(
            {"sprint_id": sprint.id}, synchronize_session="fetch"
        )
        db.session.commit()
        log = AuditLog(
            action="created",
            entity_type="Sprint",
            entity_id=sprint.id,
            old_value=None,
            new_value=f"capacity={sprint.capacity}, status={sprint.status}",
            user_id=current_user.id
        )
    db.session.add(log)
    db.session.commit()
    return redirect(url_for("homa.sprint"))


@hamed_bp.route("/tasks")
@login_required
def tasks():
    all_tasks = Task.query.order_by(Task.id).all()
    all_pbis = PBI.query.all()
    return render_template("tasks.html", tasks=all_tasks, pbis=all_pbis, role=current_user.role)


@hamed_bp.route("/tasks/add", methods=["POST"])
@login_required
def tasks_add():
    title = request.form["title"].strip()
    effort = request.form["effort"]
    pbi_id = request.form["pbi_id"]
    if title:
        try:
            task = Task(title=title, estimated_effort=float(effort), pbi_id=int(pbi_id))
            db.session.add(task)
            db.session.commit()
            log = AuditLog(
                action="created",
                entity_type="Task",
                entity_id=task.id,
                old_value=None,
                new_value=f"title={task.title}, effort={task.estimated_effort}, pbi_id={task.pbi_id}",
                user_id=current_user.id
            )
            db.session.add(log)
            db.session.commit()
        except (ValueError, KeyError):
            pass
    return redirect(url_for("hamed.tasks"))


@hamed_bp.route("/log_effort", methods=["POST"])
@login_required
def log_effort_route():
    try:
        task_id = int(request.form["task_id"])
        date_str = request.form["date"]
        actual_effort = float(request.form["actual_effort"])
        if actual_effort > 0 and date_str:
            effort_log = EffortLog(
                task_id=task_id,
                date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                hours_spent=actual_effort
            )
            db.session.add(effort_log)
            db.session.commit()
            log = AuditLog(
                action="logged",
                entity_type="EffortLog",
                entity_id=effort_log.id,
                old_value=None,
                new_value=f"task_id={task_id}, date={date_str}, hours={actual_effort}",
                user_id=current_user.id
            )
            db.session.add(log)
            db.session.commit()
    except (ValueError, KeyError):
        pass
    return redirect(url_for("hamed.tasks"))


@hamed_bp.route("/reports")
@login_required
def reports():
    sprints = Sprint.query.order_by(Sprint.id).all()
    velocity = db.session.query(
        PBI.sprint_id,
        db.func.coalesce(db.func.sum(EffortLog.hours_spent), 0)
    ).outerjoin(Task, Task.pbi_id == PBI.id)\
     .outerjoin(EffortLog, EffortLog.task_id == Task.id)\
     .filter(PBI.sprint_id.isnot(None))\
     .group_by(PBI.sprint_id).order_by(PBI.sprint_id).all()
    return render_template("reports.html", sprints=sprints, velocity=velocity)


@hamed_bp.route("/reports/<int:sprint_id>")
@login_required
def reports_sprint(sprint_id):
    Sprint.query.get_or_404(sprint_id)
    total_effort = db.session.query(
        db.func.coalesce(db.func.sum(Task.estimated_effort), 0)
    ).join(PBI, Task.pbi_id == PBI.id).filter(PBI.sprint_id == sprint_id).scalar()
    daily_logs = db.session.query(
        EffortLog.date,
        db.func.sum(EffortLog.hours_spent)
    ).join(Task, EffortLog.task_id == Task.id)\
     .join(PBI, Task.pbi_id == PBI.id)\
     .filter(PBI.sprint_id == sprint_id)\
     .group_by(EffortLog.date).order_by(EffortLog.date).all()
    velocity = db.session.query(
        PBI.sprint_id,
        db.func.coalesce(db.func.sum(EffortLog.hours_spent), 0)
    ).outerjoin(Task, Task.pbi_id == PBI.id)\
     .outerjoin(EffortLog, EffortLog.task_id == Task.id)\
     .filter(PBI.sprint_id.isnot(None))\
     .group_by(PBI.sprint_id).order_by(PBI.sprint_id).all()
    sprints = Sprint.query.order_by(Sprint.id).all()
    chart_path = generate_burndown_chart(sprint_id, total_effort, daily_logs, 14, None)
    return render_template("reports.html", sprints=sprints, velocity=velocity,
                           selected_sprint_id=sprint_id, total_effort=total_effort,
                           chart_path=chart_path)