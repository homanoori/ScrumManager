from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, PBI

atena_bp = Blueprint("atena", __name__)

@atena_bp.route("/backlog")
@login_required
def backlog():
    pbis = PBI.query.order_by(
        db.case(
            (PBI.priority == 'H', 1),
            (PBI.priority == 'M', 2),
            (PBI.priority == 'L', 3),
        ),
        PBI.effort.asc()
    ).all()
    return render_template("backlog.html", pbis=pbis, role=current_user.role)

@atena_bp.route("/backlog/add", methods=["POST"])
@login_required
def add_pbi():
    if current_user.role == "client":
        return redirect(url_for("atena.backlog"))
    title = request.form["title"]
    priority = request.form["priority"]
    effort = float(request.form["effort"])
    pbi = PBI(title=title, priority=priority, effort=effort, status="Incomplete")
    db.session.add(pbi)
    db.session.commit()
    return redirect(url_for("atena.backlog"))