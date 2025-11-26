"""
Forms for creating and deleting Register objects.

This module contains two Flask-WTF form classes used when working with
Register records:

- RegisterForm: Used when creating or editing a Register.
- RegisterDeleteForm: Used to confirm deletion of a Register.

Both forms use GOV.UK Frontend-styled WTForms widgets to match the
design system used in the application.
"""

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovSubmitInput,
    GovTextInput,
    GovCheckboxInput
)
from wtforms.fields import StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired, ValidationError

from app.models import Entry


class EntryForm(FlaskForm):
    """
    A form used to add or edit an Entry.

    Fields
    ------
    name : StringField
        The human-readable name for the Entry. This is required
        and must be unique across all Entries for a given Register.
    submit : SubmitField
        A standard submit button.

    Custom Validation
    -----------------
    validate_name(field):
        WTForms automatically looks for methods named `validate_<fieldname>`
        and calls them when that field is validated.
        This method checks whether the chosen name already exists in the
        database and raises a ValidationError if so.
    """

    # A text field for entering the register name.
    # The `GovTextInput` widget makes it appear using GOV.UK styling.
    name = StringField(
        "Name",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter a name")],
    )

    # A standard GOV.UK-styled submit button.
    submit: SubmitField = SubmitField("Save", widget=GovSubmitInput())

    def __init__(self, register_id, **kwargs):
        super().__init__(**kwargs)
        self.register_id = register_id

    def validate_name(self, field):
        """
        Ensure that the entry name is unique for the given Register.

        Parameters
        ----------
        field : wtforms.fields.StringField
            The field object containing the value entered by the user.

        Raises
        ------
        ValidationError
            If an Entry already exists with the same name within the given register.

        Notes
        -----
        - This method uses SQLAlchemy to query the database.
        - `first()` returns the first matching Entry or None.
        - Raising a ValidationError tells WTForms that this field is invalid,
          and the error message is displayed to the user.
        """
        existing = Entry.query.filter_by(register_id=self.register_id, name=field.data).first()
        if existing:
            raise ValidationError("This entry already exists.")


class EntryDeleteForm(FlaskForm):
    """
    A form used to confirm the deletion of an Entry.

    This form intentionally keeps the confirmation checkbox very explicit,
    to ensure users do not accidentally delete data.

    Fields
    ------
    confirm : BooleanField
        A checkbox that the user must tick to confirm deletion.
        If left unticked, the validation will fail and deletion will not occur.
    submit : SubmitField
        A GOV.UK-styled delete button.
    """

    # A checkbox that the user must actively tick to continue.
    # Using InputRequired ensures the user can't accidentally skip it.
    confirm = BooleanField(
        "I'm sure",
        widget=GovCheckboxInput(),
        validators=[InputRequired(message="Select if you want to delete this Entry")],
    )

    # Submit button styled using GOV.UK design system components.
    submit: SubmitField = SubmitField("Delete", widget=GovSubmitInput())