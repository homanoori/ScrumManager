# Setayesh adds her routes here
from flask import Blueprint, render_template, session, redirect, url_for, request

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