from datetime import datetime

from flask import Blueprint, current_app, g, request

from middleware.firebase_auth import auth_required
from models import Kid, db
from services.kid_service import create_kid, list_kids_for_user
from services.storage_service import generate_avatar_key, generate_presigned_upload
from utils.helpers import error_response, json_response

kid_bp = Blueprint("kids", __name__)


def _kid_belongs_to_user(kid: Kid, user) -> bool:
    if not kid or not user:
        return False
    if kid.household_id and getattr(user, "household_id", None) == kid.household_id:
        return True
    if kid.parent_user_id and getattr(user, "id", None) == kid.parent_user_id:
        return True
    return False


@kid_bp.route("", methods=["POST"])
@auth_required
def add_kid():
    payload = request.get_json(silent=True) or {}
    first_name = (payload.get("first_name") or "").strip()
    dob_raw = payload.get("dob")
    gender = payload.get("gender")
    avatar_url = payload.get("avatar_url")

    if not first_name:
        current_app.logger.warning("Kid creation failed: first_name is required")
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
        avatar_url=avatar_url,
    )

    return json_response(
        {
            "id": str(kid.id),
            "first_name": kid.first_name,
            "gender": kid.gender,
            "dob": kid.dob.isoformat() if kid.dob else None,
            "household_id": kid.household_id,
            "parent_user_id": kid.parent_user_id,
            "avatar_url": kid.avatar_url,
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
                "avatar_url": k.avatar_url,
            }
            for k in kids
        ]
    )


@kid_bp.route("/avatar/upload-url", methods=["POST"])
@auth_required
def kid_avatar_upload_url():
    payload = request.get_json(silent=True) or {}
    kid_id = (payload.get("kid_id") or "").strip()
    content_type = payload.get("content_type")
    file_name = payload.get("file_name")

    if not kid_id:
        return error_response("kid_id is required", status_code=400)

    current_user = getattr(g, "current_user", None)
    kid = Kid.query.filter_by(id=kid_id).first()
    if not kid:
        return error_response("Kid not found", status_code=404)
    if not _kid_belongs_to_user(kid, current_user):
        return error_response("Not authorized for this kid", status_code=403)

    key = generate_avatar_key("kids", kid_id, file_name)

    try:
        presigned = generate_presigned_upload(key=key, content_type=content_type)
    except RuntimeError:
        current_app.logger.exception("Failed to generate kid avatar upload URL")
        return error_response("Could not create upload URL", status_code=500)

    kid.avatar_url = presigned["public_url"]
    db.session.commit()

    return json_response(
        {
            "kid_id": kid.id,
            "upload_url": presigned["upload_url"],
            "expires_in": presigned["expires_in"],
            "key": presigned["key"],
            "avatar_url": kid.avatar_url,
        },
        status_code=201,
    )


@kid_bp.route("/<kid_id>/avatar", methods=["GET"])
@auth_required
def get_kid_avatar(kid_id: str):
    current_user = getattr(g, "current_user", None)
    kid = Kid.query.filter_by(id=kid_id).first()
    if not kid:
        return error_response("Kid not found", status_code=404)
    if not _kid_belongs_to_user(kid, current_user):
        return error_response("Not authorized for this kid", status_code=403)

    if not kid.avatar_url:
        return error_response("Avatar not set for this kid", status_code=404)

    return json_response(
        {
            "kid_id": kid.id,
            "avatar_url": kid.avatar_url,
        }
    )
