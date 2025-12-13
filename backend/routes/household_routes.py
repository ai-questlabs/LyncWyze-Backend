from flask import Blueprint, g, request

from middleware.firebase_auth import auth_required
from models import db
from services.household_service import create_household, get_household_for_user
from utils.helpers import error_response, json_response

household_bp = Blueprint("households", __name__)


@household_bp.route("", methods=["POST"])
@auth_required
def create():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    address = payload.get("address")
    location = payload.get("location")

    if not name:
        return error_response("name is required", status_code=400)

    household = create_household(name=name, address=address, location=location)

    current_user = getattr(g, "current_user", None)
    if current_user:
        current_user.household_id = household.id
        db.session.commit()

    return json_response(
        {
            "id": household.id,
            "name": household.name,
            "address": household.address,
            "location": household.location,
        },
        status_code=201,
    )


@household_bp.route("/me", methods=["GET"])
@auth_required
def get_my_household():
    current_user = getattr(g, "current_user", None)
    household = get_household_for_user(current_user)
    if not household:
        return error_response("Household not found", status_code=404)

    return json_response(
        {
            "id": household.id,
            "name": household.name,
            "address": household.address,
            "location": household.location,
        }
    )
