from flask import Blueprint, redirect, request, render_template
from flask_login import login_required
from models import db, Sprint, PBI, Task, EffortLog

homa_bp = Blueprint("homa", __name__)

@homa_bp.route("/sprint")
@login_required
def sprint():
    sprints = Sprint.query.order_by(Sprint.id).all()
    sprint_pbis = PBI.query.filter(PBI.sprint_id.isnot(None)).all()
    return render_template("sprint.html", sprints=sprints, sprint_pbis=sprint_pbis)

@homa_bp.route("/sprint/<int:sprint_id>/status", methods=["POST"])
@login_required
def update_sprint_status(sprint_id):
    sprint = Sprint.query.get_or_404(sprint_id)
    if sprint.status == "Planned":
        sprint.status = "Active"
    elif sprint.status == "Active":
        sprint.status = "Complete"
        _return_unfinished_pbis(sprint_id)
    db.session.commit()
    return redirect("/sprint")

def _return_unfinished_pbis(sprint_id):
    unfinished = PBI.query.filter_by(sprint_id=sprint_id).filter(PBI.status != "Complete").all()
    for pbi in unfinished:
        completed_effort = db.session.query(
            db.func.coalesce(db.func.sum(EffortLog.hours_spent), 0)
        ).join(Task, EffortLog.task_id == Task.id).filter(Task.pbi_id == pbi.id).scalar()
        pbi.sprint_id = None
        pbi.status = "Incomplete"
        pbi.effort = max(0, pbi.effort - completed_effort)