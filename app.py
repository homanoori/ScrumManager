from flask import Flask, render_template, session, request
from database import init_db

from routes.hamed_routes import hamed_bp
from routes.homa_routes import homa_bp
from routes.setayesh_routes import setayesh_bp
from routes.atena_routes import atena_bp

app = Flask(__name__)
app.secret_key = "secret123"

app.register_blueprint(hamed_bp)
app.register_blueprint(homa_bp)
app.register_blueprint(setayesh_bp)
app.register_blueprint(atena_bp)

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

if __name__ == "__main__":
    init_db()
    app.run(debug=True)