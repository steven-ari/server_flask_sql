import logging
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from logging.handlers import TimedRotatingFileHandler
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Create a formatter with timestamp and log level
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Configure file handler with rotation
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

file_handler = TimedRotatingFileHandler(os.path.join(log_dir, 'app.log'), when='midnight', interval=1, backupCount=7)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

with app.app_context():
    from app.api.user import bp as user_bp
    app.register_blueprint(user_bp)

    from app.api.pdf import bp as pdf_bp
    app.register_blueprint(pdf_bp, url_prefix='/pdf')

    from app.api.image import bp as image_bp
    app.register_blueprint(image_bp, url_prefix='/image')

    from app.api.category import bp as category_bp
    app.register_blueprint(category_bp, url_prefix='/category')

@app.route('/hello')
def test_page():
    return 'Hello World!'
