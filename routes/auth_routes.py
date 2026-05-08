from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user 
from flask_bcrypt import Bcrypt
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

bcrypt = Bcrypt()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            username=username,
            role=role
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=identifier).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))