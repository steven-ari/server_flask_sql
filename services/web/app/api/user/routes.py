import datetime

from flask import request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import Categories, Users
from app.api.user import bp
from utils.api import success_or_404


@bp.route('/signup', methods=["POST"])
@success_or_404
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # TODO remove when checking already happen in frontend
    if len(password) < 6:
        return {"message": "Password must be at least 6 characters"}, 400
    hashed_password = generate_password_hash(password, method="sha256")
    new_user = Users(email=email, password=hashed_password)

    # append dummy category
    new_user.categories.append(Categories(name=f"Kategorie 1", color_code="0080ff"))

    db.session.add(new_user)
    db.session.commit()

    return {"message": "User created successfully"}


@bp.route('/login', methods=["POST"])
@success_or_404
def login():
    
    # Get the username and password from the request body
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Check if the username and password are correct
    user = (
        db.session.query(Users.id, Users.email, Users.password)
        .filter_by(email=email)
        .first()
    )
    if (user is None) or not check_password_hash(user.password, password):
        return {"message": "Invalid credentials"}, 401
        
    # Create the access token with id and email as the identity
    access_token = create_access_token(
        identity={"id": user.id, "email": user.email},
        expires_delta=datetime.timedelta(minutes=100),
    )
    return access_token


@bp.route('/change-pass', methods=["POST"])
@success_or_404
def change_password():

    # Get the username and password from the request body
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    new_password = data.get("new-password")

    # TODO remove when checking already happen in frontend
    if len(new_password) < 6:
        return {"message": "Password must be at least 6 characters"}, 400

    # Check if the username and password are correct
    user = Users.query.filter_by(email=email).first()
    if (user is None) or not check_password_hash(user.password, password):
        return {"message": "Invalid credentials"}, 401

    user.password = generate_password_hash(new_password, method="sha256")
    db.session.commit()

    return {"message": "Password changed"}, 200
