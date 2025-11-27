"""
Application factory and extension initialization for the Flask app.

This module defines the application factory (`create_app`) and initializes
all Flask extensions. It also registers blueprints and configures
templates and middleware.

Notes for Students:
- Flask uses an "application factory" pattern to create app instances.
- Extensions like SQLAlchemy, CSRFProtect, Limiter, and Migrate are
  initialized here but attached to the app later with `init_app`.
- Blueprints are modular components of the app; each blueprint
  groups related routes, templates, and static files.
- The template loader is configured to allow searching multiple locations
  for templates, including GOV.UK frontend templates.
"""

from typing import Type

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect  # type: ignore[import]
from govuk_frontend_wtf.main import WTFormsHelpers  # type: ignore[import]
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

# --- FLASK EXTENSIONS ---
#
# These are initialized once here so they can be imported elsewhere in the app.
# They will be "attached" to the app later using `init_app`.
csrf: CSRFProtect = CSRFProtect()
db: SQLAlchemy = SQLAlchemy()
limiter: Limiter = Limiter(
    get_remote_address,
    default_limits=["50 per second", "500 per minute"],  # Rate limits for requests
)
migrate: Migrate = Migrate()


def create_app(config_class: Type[Config] = Config) -> Flask:
    """
    Application factory to create and configure the Flask app.

    Args:
        config_class: The configuration class to use (defaults to `Config`).

    Returns:
        A configured Flask application instance.
    """
    # Create the Flask application instance
    app: Flask = Flask(__name__)  # type: ignore[assignment]
    app.config.from_object(config_class)

    # --- JINJA2 TEMPLATE CONFIG ---
    # Add a global variable to the template environment
    app.jinja_env.globals["govukRebrand"] = True
    # Strip and trim blocks to remove extra whitespace in rendered templates
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    # Configure template loaders to allow multiple template sources
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),  # Load templates from the 'app' package
            PrefixLoader(
                {
                    # Load templates from GOV.UK frontend packages
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # --- MIDDLEWARE ---
    # ProxyFix handles headers from reverse proxies like Nginx or load balancers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[method-assign]

    # --- INITIALIZE EXTENSIONS ---
    # Attach extensions to this Flask app
    csrf.init_app(app)  # CSRF protection for forms
    db.init_app(app)  # SQLAlchemy database connection
    limiter.init_app(app)  # Rate limiting for requests
    migrate.init_app(app, db)  # Database migrations
    WTFormsHelpers(app)  # Add GOV.UK WTForms helpers for forms

    # --- REGISTER BLUEPRINTS ---
    # Blueprints group related routes and templates
    from app.main import bp as main_bp
    from app.register import bp as register_bp
    from app.login import bp as login_bp

    # Register the main blueprint for generic routes
    app.register_blueprint(main_bp)
    # Register the Register blueprint (including nested Entry blueprint)
    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)

    return app


# Import models to ensure they are registered with SQLAlchemy
# noqa disables warnings about import order or unused import
from app import models  # noqa: E402,F401
