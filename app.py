from flask import Flask, render_template, session, request
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User
from routes.auth_routes import auth_bp
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

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(hamed_bp)
app.register_blueprint(homa_bp)
app.register_blueprint(setayesh_bp)
app.register_blueprint(atena_bp)
app.register_blueprint(auth_bp)

# --- Atena: base route ---
@app.route("/")
@login_required
def index():
    approval_message = session.pop("approval_message", None)

    return render_template(
        "base.html",
        username=current_user.username,
        role=current_user.role,
        approval_message=approval_message
    )

with app.app_context():
    db.create_all()
    
@app.route("/run-migrations")
def run_migrations():
    from flask_migrate import upgrade
    upgrade()
    return "Migrations applied!"

if __name__ == "__main__":
    app.run(debug=True)