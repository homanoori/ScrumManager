from flask import Flask, render_template, session, request
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db
import os

from routes.hamed_routes import hamed_bp
from routes.homa_routes import homa_bp
from routes.setayesh_routes import setayesh_bp
from routes.atena_routes import atena_bp

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-secret")
db.init_app(app)
migrate = Migrate(app, db)

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
    app.run(debug=True)