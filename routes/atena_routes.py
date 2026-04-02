from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_connection

atena_bp = Blueprint("atena", __name__)

@atena_bp.route("/backlog")
def backlog():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, priority, effort, status, sprint_id FROM pbi ORDER BY CASE priority WHEN 'H' THEN 1 WHEN 'M' THEN 2 WHEN 'L' THEN 3 END, effort ASC")
    pbis = cursor.fetchall()
    conn.close()
    role = session.get("role")
    return render_template("backlog.html", pbis=pbis, role=role)

@atena_bp.route("/backlog/add", methods=["POST"])
def add_pbi():
    role = session.get("role")
    if role == "client":
        return redirect(url_for("atena.backlog"))
    title = request.form["title"]
    priority = request.form["priority"]
    effort = request.form["effort"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pbi (title, priority, effort, status) VALUES (?, ?, ?, 'Incomplete')", (title, priority, effort))
    conn.commit()
    conn.close()
    return redirect(url_for("atena.backlog"))