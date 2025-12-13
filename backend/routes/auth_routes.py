from flask import Blueprint, request

from utils.helpers import json_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    # Firebase Auth should be handled on the client; this is a placeholder
    payload = request.get_json(silent=True) or {}
    return json_response(
        {
            "message": "Use Firebase client SDK to obtain ID token; send as Bearer token to protected endpoints.",
            "echo": payload,
        }
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    return json_response({"message": "Registration handled via Firebase; ensure ID token is sent", "echo": payload})
