from flask import Blueprint

bp = Blueprint('pdf', __name__)

from app.api.pdf import routes
