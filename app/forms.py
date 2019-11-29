import os
import re
import json

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    SelectField,
    FileField,
)

from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    EqualTo,
    Length,
    regexp,
)
from werkzeug import secure_filename

from app.models import User, ScriptType


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

        # EMAIL_DOMAINS should be a pipe delimited list of allowed email
        # domains for new users to register.  If no variable is defined
        # no validation is performed.
        valid_domains = os.environ.get("EMAIL_DOMAINS")
        if valid_domains and email.data.split("@")[1] not in valid_domain.split("|"):
            raise ValidationError("Email address must be from a valid domain.")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Invalid username.")


class UploadForm(FlaskForm):
    script_type = SelectField(
        "Form Type",
        choices=[("QA", "Quality Assurance"), ("T", "Task"), ("R", "Report")],
    )
    notebook = FileField("Notebook File", validators=[FileAllowed(["ipynb"])])
    parameters = TextAreaField("Parameter JSON", validators=[Length(min=0, max=1024)])
    submit = SubmitField("Submit")

    def validate_parameters(self, parameters):
        # It's OP for there to be no data, not all notebooks have
        # parameters.
        if len(parameters.data) == 0:
            return

        try:
            ps = json.loads(parameters.data)
        except json.decoder.JSONDecodeError as e:
            raise Exception("Parameters field is not valid JSON. {}".format(e))
