"""
Blueprint: Register management (list, create, view, edit, delete)

This module defines the route handlers (also called "view functions")
for working with `Register` records in the application. It follows a
typical CRUD pattern:

- index():   List all registers
- create():  Create a new register
- view():    Display a single register by ID
- edit():    Update an existing register
- delete():  Delete an existing register

Notes for students:
- Each function below is a "view function". Flask calls it when a
  matching URL is requested by the user.
- The function must return either:
    1. HTML (via render_template), or
    2. A redirect response (for example, after a successful POST)
- `<uuid:register_id>` in the URL ensures:
    - The parameter is a valid UUID
    - Flask converts it automatically into a Python `UUID` object
"""

from uuid import UUID

from flask import flash, redirect, render_template, request, url_for
from werkzeug import Response

from app import db
from app.models import Register
from app.register import bp
from app.register.forms import RegisterDeleteForm, RegisterForm

# --- ROUTES FOR REGISTER CRUD OPERATIONS ---
#
# These routes form the "Register" section of the app.
# They are grouped under the `/registers` URL prefix
# by the blueprint defined in `app.register.__init__.py`.
# Each route corresponds to one CRUD operation.


@bp.route("/", methods=["GET"])
def index() -> str:
    """
    List all Register records.

    HTTP Method:
    - GET: Show the list of registers to the user

    Returns:
    - str: The rendered HTML page showing all registers
    """
    # Construct a SQL query to fetch all registers from the database.
    # db.select(Register) builds the SELECT query
    # .scalars() converts the results into Register objects
    # .all() loads all rows into a Python list
    registers = db.session.execute(db.select(Register)).scalars().all()

    # Render a Jinja template and pass the list of registers to it
    return render_template("register/index.html", registers=registers)


@bp.route("/new", methods=["GET", "POST"])
def create() -> str | Response:
    """
    Create a new Register.

    HTTP Methods:
    - GET: Display a blank form to the user
    - POST: Validate the form and create a new Register if valid

    Returns:
    - str: Rendered form page on GET or validation failure
    - Response: Redirect to index on successful creation
    """
    form = RegisterForm()

    # Flask-WTF handles form validation and CSRF protection for us.
    # We don't need to manually check request.form or HTML inputs.
    if form.validate_on_submit():
        # Create a new Register object with the submitted name
        register = Register(name=form.name.data)

        # Stage the new record for insertion
        db.session.add(register)
        # Commit writes the new record to the database
        db.session.commit()

        # flash() stores a one-time message in the session
        # It will be displayed on the next page load using the template
        flash("Successfully created register", "success")

        # Redirect to follow the Post/Redirect/Get (PRG) pattern
        # This prevents duplicate form submissions if the user refreshes
        return redirect(url_for("register.index"))

    # Render the form for GET requests or if validation fails
    return render_template("register/create.html", form=form)


@bp.route("/<uuid:register_id>", methods=["GET"])
def view(register_id: UUID) -> str:
    """
    View a single Register by its UUID.

    Parameters:
    - register_id (UUID): The unique identifier of the Register

    Returns:
    - str: Rendered HTML page showing the register details
    """
    # Fetch the register or return a 404 page if it does not exist
    register = db.get_or_404(Register, register_id)

    # Render the detail page for this register
    return render_template("register/view.html", register=register)


@bp.route("/<uuid:register_id>/edit", methods=["GET", "POST"])
def edit(register_id: UUID) -> str | Response:
    """
    Edit an existing Register.

    HTTP Methods:
    - GET: Pre-populate the form with current register data
    - POST: Validate and update the register if the form is valid

    Parameters:
    - register_id (UUID): The unique identifier of the Register to edit

    Returns:
    - str: Rendered form page if GET or validation fails
    - Response: Redirect to index on successful edit
    """
    # Load the register or show 404 if it doesn't exist
    register: Register = db.get_or_404(Register, register_id)
    form = RegisterForm()

    if request.method == "GET":
        # Pre-fill the form with current data so user can edit it
        form.name.data = register.name
    elif form.validate_on_submit():
        # Copy validated form data into the Register object
        register.name = form.name.data

        # Persist changes to the database
        db.session.commit()

        flash("Successfully updated register", "success")
        return redirect(url_for("register.view", register_id=register_id))

    # Render the form page for GET requests or failed validation
    return render_template("register/edit.html", register=register, form=form)


@bp.route("/<uuid:register_id>/delete", methods=["GET", "POST"])
def delete(register_id: UUID) -> str | Response:
    """
    Delete an existing Register.

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
    register = db.get_or_404(Register, register_id)

    if register and register.entries:
        flash(f"<b>You cannot delete a register with entries.", "Error")
        return redirect(url_for("register.view", register_id=register_id))

    form = RegisterDeleteForm()

    if form.validate_on_submit():
        error = None

        if register.entries:
            error = "This register has entries."

        if error:
            flash(f"<b>Could not delete register '{register.name}'</b>: {error}", "Error")
            return redirect(url_for("register.index"))
        
        # Remove the register from the database
        db.session.delete(register)
        db.session.commit()

        flash("Successfully deleted register", "success")
        return redirect(url_for("register.index"))

    # Render the confirmation page if GET request or validation fails
    return render_template("register/delete.html", register=register, form=form)
