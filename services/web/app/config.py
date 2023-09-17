import os
from pathlib import Path

UPLOAD_FOLDER = Path.cwd().parents[1] / "assets"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)
