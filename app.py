from flask import Flask, render_template, session, redirect, url_for, request
from database import init_db

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

@app.route('/approve')
def approve():
    role = session.get('role')

    if role != 'client':
        session['approval_message'] = "Only the client can approve sprint scope changes."
        return redirect(url_for('index'))

    session['approval_message'] = "Sprint approved successfully."
    return redirect(url_for('index'))

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