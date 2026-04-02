from flask import Flask, render_template, session, redirect, url_for, request
from datetime import datetime
from database import init_db, get_or_create_user, add_approval, get_all_tasks, get_all_pbis, update_task_status

app = Flask(__name__)
app.secret_key = "secret123"


# --- Atena: base route ---
@app.route("/")
def index():
    username = session.get("username")
    role = session.get("role")
    approval_message = session.pop("approval_message", None)
    return render_template(
        "base.html",
        username=username,
        role=role,
        approval_message=approval_message
    )


# --- Setayesh: login route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']

        session['username'] = username
        session['role'] = role

        return redirect(url_for('index'))

    return render_template('login.html')


# --- Setayesh: approval route ---
@app.route('/approve/<int:sprint_id>')
def approve(sprint_id):
    role = session.get('role')
    username = session.get('username')

    if role != 'client':
        session['approval_message'] = "Only the client can approve sprint scope changes."
        return redirect(url_for('index'))

    user_id = get_or_create_user(username, role)
    approved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    add_approval(user_id, sprint_id, approved_at)

    session['approval_message'] = "Sprint approved successfully."
    return redirect(url_for('index'))


# --- Setayesh: tasks page ---
@app.route('/tasks')
def tasks():
    tasks = get_all_tasks()
    pbis = get_all_pbis()
    return render_template('tasks.html', tasks=tasks, pbis=pbis)


# --- Setayesh: task status update ---
@app.route('/task/update-status/<int:task_id>', methods=['POST'])
def change_task_status(task_id):
    new_status = request.form['status']
    update_task_status(task_id, new_status)
    return redirect(url_for('tasks'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- Hamed: add burndown + sprint proposal routes in his branch ---

# --- Homa: add sprint lock + status change routes in her branch ---

# --- Sasan: add client view routes in his branch ---


if __name__ == "__main__":
    init_db()
    app.run(debug=True)