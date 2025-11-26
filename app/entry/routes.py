"""
Blueprint: Entry management (list, create, view, edit, delete)

This module defines the route handlers (also called "view functions")
for working with `Entry` records in the application. It follows a
typical CRUD pattern:

- index():   List all entries in a specific register
- create():  Create a new entry in a specific register
- view():    Display a single entry by ID in a specific register
- edit():    Update an existing entry in a specific register
- delete():  Delete an existing entry in a specific register
"""

from uuid import UUID

from flask import flash, redirect, render_template, url_for, request
from werkzeug import Response

from app import db
from app.entry import bp
from app.entry.forms import EntryForm, EntryDeleteForm
from app.models import Entry


@bp.route("/add", methods=["GET", "POST"])
def add(register_id: UUID) -> str | Response:
    form = EntryForm(register_id=register_id)

    # Flask-WTF handles form validation and CSRF protection for us.
    # We don't need to manually check request.form or HTML inputs.
    if form.validate_on_submit():
        entry = Entry(name=form.name.data, register_id=register_id)
        db.session.add(entry)
        db.session.commit()
        flash("Successfully added entry to register", "success")

        # Redirect to follow the Post/Redirect/Get (PRG) pattern
        # This prevents duplicate form submissions if the user refreshes
        return redirect(url_for("register.view", register_id=register_id))

    # Render the form for GET requests or if validation fails
    return render_template("entry/add.html", form=form)


@bp.route("/<uuid:entry_id>", methods=["GET"])
def view(register_id: UUID, entry_id: UUID) -> str:
    """
    View a single Entry by its UUID.

    Parameters:
    - register_id (UUID): The unique identifier of the Register
    - entry_id (UUID): The unique identifier of the Entry

    Returns:
    - str: Rendered HTML page showing the register entry details
    """
    # Fetch the entry or return a 404 page if it does not exist
    entry = db.one_or_404(db.select(Entry).filter_by(register_id=register_id, id=entry_id))

    # Render the detail page for this register
    return render_template("entry/view.html", entry=entry)

@bp.route("/<uuid:entry_id>/edit", methods=["GET", "POST"])
def edit(register_id: UUID, entry_id: UUID) -> str | Response:
    """
    Edit an existing Entry.

    HTTP Methods:
    - GET: Pre-populate the form with current entry data
    - POST: Validate and update the entry if the form is valid

    Parameters:
    - register_id (UUID): The unique identifier of the  to edit

    Returns:
    - str: Rendered form page if GET or validation fails
    - Response: Redirect to index on successful edit
    """
    # Load the register or show 404 if it doesn't exist
    entry: Entry = db.get_or_404(Entry, entry_id)
    form = EntryForm(register_id)

    if request.method == "GET":
        # Pre-fill the form with current data so user can edit it
        form.name.data = entry.name
    elif form.validate_on_submit():
        # Copy validated form data into the Register object
        entry.name = form.name.data

        # Persist changes to the database
        db.session.commit()

        flash("Successfully updated entry", "success")
        return redirect(url_for("register.view", entry_id=entry_id, register_id=register_id))

    # Render the form page for GET requests or failed validation
    return render_template("entry/edit.html", entry=entry, form=form, register_id=register_id)


@bp.route("/<uuid:entry_id>/delete", methods=["GET", "POST"])
def delete(register_id: UUID, entry_id: UUID) -> str | Response:
    """
    Delete an existing entry.

    HTTP Methods:
    - GET: Show a confirmation page to avoid accidental deletion
    - POST: Delete the register if confirmation is given

    Parameters:
    - register_id (UUID): The unique identifier of the Register to delete

    Returns:
    - str: Rendered confirmation page if GET or validation fails
    - Response: Redirect to index on successful deletion
    """
    # Load the register to delete or return 404 if not found
    entry = db.get_or_404(Entry, entry_id)

    form = EntryDeleteForm()

    if form.validate_on_submit():
        # Remove the register from the database
        db.session.delete(entry)
        db.session.commit()

        flash("Successfully deleted entry", "success")
        return redirect(url_for("register.view", entry_id=entry_id, register_id=register_id))

    # Render the confirmation page if GET request or validation fails
    return render_template("entry/delete.html", entry=entry, form=form)

