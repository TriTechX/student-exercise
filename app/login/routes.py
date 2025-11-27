from uuid import UUID

from flask import flash, redirect, render_template, url_for, request, session
from werkzeug import Response

from app import db
from app.login import bp
from app.login.forms import NewAccountForm, LoginForm
from app.models import Users

from argon2 import PasswordHasher
hasher = PasswordHasher()


@bp.route("/", methods=["GET", "POST"])
def index() -> str | Response:
    form = LoginForm()

    if form.validate_on_submit():
        user = Users(username=form.username.data, password=form.password.data)

        ## sign in as this user and store the session token
        session["user_id"] = str(user.id)
        session["username"] = str(user.username)

        flash(f"Welcome back, {form.username.data}.", "success")
        return redirect(url_for("main.index"))

    return render_template("login/index.html", form=form)

@bp.route("/signup", methods=["GET", "POST"])
def create() -> str | Response:
    form = NewAccountForm()

    if form.validate_on_submit():
        user = Users(username=form.username.data, password=hasher.hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash("User successfully created.", "success")

        return redirect(url_for("main.index"))

    return render_template("login/signup.html", form=form)

@bp.route("/logout", methods=["GET"])
def logout() -> str | Response:
    if session:
        session["user_id"] = None
        session["username"] = None

        flash("Successfully logged out.", "Success")
        return redirect(url_for("main.index"))
