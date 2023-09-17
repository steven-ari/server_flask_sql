from flask import Blueprint

bp = Blueprint('category', __name__)

from app.api.category import routes
