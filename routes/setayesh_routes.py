from flask import Blueprint, redirect, url_for, request, session
from flask_login import login_required, current_user
from models import db, Task, PBI

setayesh_bp = Blueprint("setayesh", __name__)

@setayesh_bp.route('/approve')
@login_required
def approve():
    if current_user.role != 'client':
        session['approval_message'] = "Only the client can approve sprint scope changes."
        return redirect(url_for('index'))
    session['approval_message'] = "Sprint approved successfully."
    return redirect(url_for('index'))

@setayesh_bp.route('/tasks/update_status', methods=['POST'])
@login_required
def update_task_status():
    task_id = int(request.form['task_id'])
    new_status = request.form['status']
    task = Task.query.get_or_404(task_id)
    task.status = new_status
    db.session.flush()
    incomplete = Task.query.filter_by(pbi_id=task.pbi_id).filter(Task.status != 'Done').count()
    if incomplete == 0:
        pbi = PBI.query.get(task.pbi_id)
        if pbi:
            pbi.status = 'Complete'
    db.session.commit()
    return redirect(url_for('hamed.tasks'))