from flask import Blueprint

bp = Blueprint('image', __name__)

from app.api.image import routes
