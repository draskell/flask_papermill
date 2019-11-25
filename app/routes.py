from datetime import datetime

from flask import request
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app.models import User
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/")
@app.route("/index")
@login_required
def index():
    """
    Index page to 
    """
    user = {"username": "draskell"}
    jupyter_templates = [
        {
            "name": "This Template",
            "description": "This template does the thing that this template does.",
        },
        {
            "name": "That Template",
            "description": "That template does the thing that that template does.",
        },
    ]
    return render_template(
        "index.html", title="Home", jupyter_templates=jupyter_templates
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login view.
    """
    # If the user is already authenticated redirect the
    # user to the index page.
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # Render the form.
    form = LoginForm()
    if form.validate_on_submit():
        # Get the user object.
        user = User.query.filter_by(username=form.username.data).first()

        # If the user doesn't exist or the password is
        # invalid redirect to login again.
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        # Otherwise log the user in.
        login_user(user, remember=form.remember_me.data)

        # Check for a "next" argument in the request.
        next_page = request.args.get("next")

        # If there is no nextpage argument in the URL or
        # if the next_page url is to a URL that includes a
        # domain, redirect to the index.
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")

        # Otherwise redirect to the next page.
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    """
    Logout view.
    """
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    """
    User page view function.  
    
    TODO: This page will eventually be used to show the user
    links to the results of their previously run notebooks.
    """

    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "Test post #2"},
    ]
    return render_template("user.html", user=user, posts=posts)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)

