from flask import Blueprint, current_app, g, request

from middleware.firebase_auth import auth_required
from models import Household, db
from services.household_service import create_household, get_household_for_user
from services.storage_service import generate_avatar_key, generate_presigned_upload
from utils.helpers import error_response, json_response

household_bp = Blueprint("households", __name__)


def _authorize_household_access(household_id: str, user):
    if not household_id or not user:
        return None, "household_id is required"

    household = Household.query.filter_by(id=household_id).first()
    if not household:
        return None, "Household not found"

    if getattr(user, "household_id", None) != household.id:
        return None, "Not authorized for this household"

    return household, None


@household_bp.route("", methods=["POST"])
@auth_required
def create():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    address = payload.get("address")
    phone = payload.get("phone")
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    latitude = float(latitude) if latitude not in (None, "") else None
    longitude = float(longitude) if longitude not in (None, "") else None

    if not name:
        return error_response("name is required", status_code=400)

    household = create_household(
        name=name,
        address=address,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
    )

    current_user = getattr(g, "current_user", None)
    if current_user:
        current_user.household_id = household.id
        db.session.commit()

    return json_response(
        {
            "id": household.id,
            "name": household.name,
            "address": household.address,
            "phone": household.phone,
            "latitude": household.latitude,
            "longitude": household.longitude,
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
            "phone": household.phone,
            "latitude": household.latitude,
            "longitude": household.longitude,
        }
    )


@household_bp.route("/avatar/upload-url", methods=["POST"])
@auth_required
def household_avatar_upload_url():
    payload = request.get_json(silent=True) or {}
    provided_household_id = payload.get("household_id")
    content_type = payload.get("content_type")
    file_name = payload.get("file_name")

    current_user = getattr(g, "current_user", None)
    household_id = provided_household_id or getattr(current_user, "household_id", None)
    household, error = _authorize_household_access(household_id, current_user)
    if error:
        status = 404 if error == "Household not found" else 403 if "Not authorized" in error else 400
        return error_response(error, status_code=status)

    key = generate_avatar_key("households", household.id, file_name)

    try:
        presigned = generate_presigned_upload(key=key, content_type=content_type)
    except RuntimeError:
        current_app.logger.exception("Failed to generate household avatar upload URL")
        return error_response("Could not create upload URL", status_code=500)

    household.avatar_url = presigned["public_url"]
    db.session.commit()

    return json_response(
        {
            "household_id": household.id,
            "upload_url": presigned["upload_url"],
            "expires_in": presigned["expires_in"],
            "key": presigned["key"],
            "avatar_url": household.avatar_url,
        },
        status_code=201,
    )


@household_bp.route("/<household_id>/avatar", methods=["GET"])
@auth_required
def get_household_avatar(household_id: str):
    current_user = getattr(g, "current_user", None)
    household, error = _authorize_household_access(household_id, current_user)
    if error:
        status = 404 if error == "Household not found" else 403 if "Not authorized" in error else 400
        return error_response(error, status_code=status)

    if not household.avatar_url:
        return error_response("Avatar not set for this household", status_code=404)

    return json_response(
        {
            "household_id": household.id,
            "avatar_url": household.avatar_url,
        }
    )
