from flask import Blueprint, g

from middleware.firebase_auth import auth_required
from utils.helpers import json_response

user_bp = Blueprint("users", __name__)


@user_bp.route("/me", methods=["GET"])
@auth_required
def me():
    user = getattr(g, "current_user", None)
    if not user:
        return json_response({"error": "User not found"}, status_code=404)

    return json_response(
        {
            "id": str(user.id) if getattr(user, "id", None) else None,
            "firebase_uid": user.firebase_uid,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
        }
    )
