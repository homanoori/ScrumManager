# app.py
from flask import Flask, render_template
from database import init_db

app = Flask(__name__)

# --- Atena: base route ---
@app.route("/")
def index():
    return render_template("base.html")

# --- Hamed: add burndown + sprint proposal routes in his branch ---

# --- Homa: add sprint lock + status change routes in her branch ---

# --- Setayesh: add login + approval + task status routes in her branch ---

# --- Sasan: add client view routes in his branch ---

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
