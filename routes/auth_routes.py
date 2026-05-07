from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from flask_bcrypt import Bcrypt
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

bcrypt = Bcrypt()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "developer")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return "Register route works"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return "Login route works"


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))