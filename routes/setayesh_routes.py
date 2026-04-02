# Setayesh adds her routes here
from flask import Blueprint, render_template, session, redirect, url_for, request
from database import get_connection

setayesh_bp = Blueprint("setayesh", __name__)


@setayesh_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        session['username'] = username
        session['role'] = role
        return redirect(url_for('index'))
    return render_template('login.html')


@setayesh_bp.route('/approve')
def approve():
    role = session.get('role')
    if role != 'client':
        session['approval_message'] = "Only the client can approve sprint scope changes."
        return redirect(url_for('index'))
    session['approval_message'] = "Sprint approved successfully."
    return redirect(url_for('index'))


@setayesh_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@setayesh_bp.route('/tasks/update_status', methods=['POST'])
def update_task_status():
    task_id = request.form['task_id']
    new_status = request.form['status']
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE task SET status = ? WHERE id = ?", (new_status, task_id))
    c.execute("SELECT pbi_id FROM task WHERE id = ?", (task_id,))
    pbi_id = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM task WHERE pbi_id = ? AND status != 'Done'", (pbi_id,))
    incomplete_count = c.fetchone()[0]
    if incomplete_count == 0:
        c.execute("UPDATE pbi SET status = 'Complete' WHERE id = ?", (pbi_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('hamed.tasks'))