from datetime import datetime

from flask import Blueprint, g, request

from middleware.firebase_auth import auth_required
from services.kid_service import create_kid, list_kids_for_user
from utils.helpers import error_response, json_response

kid_bp = Blueprint("kids", __name__)


@kid_bp.route("", methods=["POST"])
@auth_required
def add_kid():
    payload = request.get_json(silent=True) or {}
    first_name = (payload.get("first_name") or "").strip()
    dob_raw = payload.get("dob")
    gender = payload.get("gender")

    if not first_name:
        return error_response("first_name is required", status_code=400)

    dob = None
    if dob_raw:
        try:
            dob = datetime.fromisoformat(str(dob_raw)).date()
        except ValueError:
            return error_response("dob must be ISO date (YYYY-MM-DD)", status_code=400)

    current_user = getattr(g, "current_user", None)
    household_id = payload.get("household_id") or getattr(current_user, "household_id", None)
    parent_user_id = getattr(current_user, "id", None)

    if not household_id:
        return error_response("household_id is required (either on user or payload)", status_code=400)

    kid = create_kid(
        first_name=first_name,
        household_id=household_id,
        parent_user_id=parent_user_id,
        dob=dob,
        gender=gender,
    )

    return json_response(
        {
            "id": str(kid.id),
            "first_name": kid.first_name,
            "gender": kid.gender,
            "dob": kid.dob.isoformat() if kid.dob else None,
            "household_id": kid.household_id,
            "parent_user_id": kid.parent_user_id,
        },
        status_code=201,
    )


@kid_bp.route("", methods=["GET"])
@auth_required
def list_kids():
    current_user = getattr(g, "current_user", None)
    household_id = request.args.get("household_id") or getattr(current_user, "household_id", None)
    parent_user_id = getattr(current_user, "id", None)

    kids = list_kids_for_user(household_id=household_id, parent_user_id=parent_user_id)

    return json_response(
        [
            {
                "id": str(k.id),
                "first_name": k.first_name,
                "gender": k.gender,
                "dob": k.dob.isoformat() if k.dob else None,
                "household_id": k.household_id,
                "parent_user_id": k.parent_user_id,
            }
            for k in kids
        ]
    )
