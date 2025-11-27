from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovSubmitInput,
    GovTextInput,
    GovCheckboxInput,
    GovPasswordInput
)
from wtforms.fields import StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired, ValidationError

from app.models import Users
from argon2 import PasswordHasher

class NewAccountForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = StringField(
        "Username",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter a username.")],
    )

    password = StringField(
        "Password",
        widget=GovPasswordInput(),
        validators=[InputRequired(message="Please enter a password.")],
    )

    def validate_username(self, field):
        existing = Users.query.filter_by(username=field.data).first()

        if existing:
            raise ValidationError("This username is already in use.")

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

    submit: SubmitField = SubmitField("Create Account", widget=GovSubmitInput())

class LoginForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = StringField(
        "Username",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter a username")],
    )

    password = StringField(
        "Password",
        widget=GovPasswordInput(),
        validators=[InputRequired(message="Enter a password")],
    )

    def validate_username(self, field):
        existing = Users.query.filter_by(username=field.data).first()

        if not existing:
            raise ValidationError("Username does not exist")

    def validate_password(self, field):
        existing = Users.query.filter_by(username=self.username.data).first()

        if existing:
            hasher = PasswordHasher()

            try:
                hasher.verify(existing.password, field.data)
            except:
                raise ValidationError("Incorrect password.")

    submit: SubmitField = SubmitField("Sign In", widget=GovSubmitInput())
