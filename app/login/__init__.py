from flask import Blueprint
bp: Blueprint = Blueprint("login", __name__, url_prefix="/login")
from app.login import routes
