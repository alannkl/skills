from flask import Blueprint, jsonify, request

from . import mail
from .models import create_user, create_reset_token

bp = Blueprint("main", __name__)


@bp.post("/signup")
def signup():
    user = create_user(request.json["email"], request.json["password"])
    mail.send(user.email, "Welcome to Tally", f"Hi {user.name or 'there'}, thanks for signing up.")
    return jsonify(id=user.id), 201


@bp.post("/password-reset")
def password_reset():
    token = create_reset_token(request.json["email"])
    if token:
        mail.send(request.json["email"], "Reset your password", f"https://tally.example/reset/{token}")
    return "", 204
