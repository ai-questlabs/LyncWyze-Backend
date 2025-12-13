from functools import wraps
from typing import Any, Dict, Optional

from firebase_admin import auth
from flask import current_app, g

from models import User
from services.user_service import get_or_create_user
from utils.helpers import error_response, get_bearer_token


def _verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return auth.verify_id_token(token)
    except Exception:  # noqa: BLE001
        return None


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.config.get("AUTH_DEV_BYPASS"):
            g.current_user = User(firebase_uid="dev-bypass", email="dev@example.com")
            return func(*args, **kwargs)

        token = get_bearer_token()
        if not token:
            return error_response("Missing bearer token", status_code=401)

        decoded = _verify_token(token)
        if not decoded:
            return error_response("Invalid or expired token", status_code=401)

        firebase_uid = decoded.get("uid")
        if not firebase_uid:
            return error_response("Token missing uid", status_code=401)

        user = get_or_create_user(
            firebase_uid=firebase_uid,
            email=decoded.get("email"),
            first_name=decoded.get("name"),
        )
        g.current_user = user
        return func(*args, **kwargs)

    return wrapper
