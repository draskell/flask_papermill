from flask import render_template, flash, redirect, url_for

from app import app
from app.forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
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
        "index.html", title="Home", user=user, jupyter_templates=jupyter_templates
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)
