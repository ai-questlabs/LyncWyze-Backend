from datetime import date, time
from typing import Dict, List, Optional, Tuple, Union

from flask import Blueprint, g, request

from middleware.firebase_auth import auth_required
from models import (
    Activity,
    ActivityDayTime,
    ActivitySchedule,
    Kid,
    KidActivityEnrollment,
    db,
)
from utils.helpers import error_response, json_response

activity_bp = Blueprint("activities", __name__)


def _parse_date(value: Optional[str], field: str) -> Tuple[Optional[date], Optional[str]]:
    if value is None:
        return None, f"{field} is required"
    try:
        return date.fromisoformat(str(value)), None
    except ValueError:
        return None, f"{field} must be ISO date (YYYY-MM-DD)"


def _parse_time(value: Optional[str], field: str) -> Tuple[Optional[time], Optional[str]]:
    if value is None:
        return None, None
    try:
        parsed = time.fromisoformat(str(value))
        return parsed.replace(second=0, microsecond=0), None
    except ValueError:
        return None, f"{field} must be HH:MM (24h)"


def _parse_float(value: Optional[Union[str, float, int]], field: str) -> Tuple[Optional[float], Optional[str]]:
    if value in (None, ""):
        return None, None
    try:
        return float(value), None
    except (TypeError, ValueError):
        return None, f"{field} must be a number"


def _format_time(value: Optional[time]) -> Optional[str]:
    if not value:
        return None
    return value.strftime("%H:%M")


def _ensure_weekdays(raw_weekdays: Optional[List[int]], schedule_type: str, start_date: date) -> Tuple[List[int], Optional[str]]:
    if raw_weekdays in (None, []):
        if schedule_type == "recurring":
            return [], "weekdays is required for recurring schedules"
        # one_time: default to the start_date weekday
        return [start_date.weekday()], None

    weekdays: List[int] = []
    for w in raw_weekdays:
        try:
            w_int = int(w)
        except (TypeError, ValueError):
            return [], "weekdays must be integers between 0 and 6"
        if w_int < 0 or w_int > 6:
            return [], "weekdays must be between 0 (Monday) and 6 (Sunday)"
        if w_int not in weekdays:
            weekdays.append(w_int)
    return sorted(weekdays), None


def _validate_schedule(payload: Dict[str, object]) -> Tuple[Optional[Dict[str, object]], Optional[str]]:
    schedule_type = str(payload.get("schedule_type") or "").lower()
    if schedule_type not in {"one_time", "recurring"}:
        return None, "schedule_type must be 'one_time' or 'recurring'"

    start_date, err = _parse_date(payload.get("start_date"), "start_date")
    if err:
        return None, err
    end_date_raw = payload.get("end_date")
    if end_date_raw:
        end_date, err = _parse_date(end_date_raw, "end_date")
        if err:
            return None, err
    else:
        end_date = start_date

    if end_date < start_date:
        return None, "end_date cannot be before start_date"

    tz = payload.get("timezone")
    if not tz or not isinstance(tz, str):
        return None, "timezone is required"

    weekdays, err = _ensure_weekdays(payload.get("weekdays"), schedule_type, start_date)
    if err:
        return None, err

    default_start_time, err = _parse_time(payload.get("start_time"), "start_time")
    if err:
        return None, err
    default_end_time, err = _parse_time(payload.get("end_time"), "end_time")
    if err:
        return None, err

    if default_start_time and default_end_time and default_end_time <= default_start_time:
        return None, "end_time must be after start_time"

    day_times_payload = payload.get("day_times") or []
    day_times: List[Dict[str, object]] = []
    for entry in day_times_payload:
        if not isinstance(entry, dict):
            return None, "day_times must be a list of objects"
        weekday, err = _ensure_weekdays([entry.get("weekday")], schedule_type, start_date)
        if err:
            return None, err
        parsed_start, err = _parse_time(entry.get("start_time"), "day_times.start_time")
        if err:
            return None, err
        parsed_end, err = _parse_time(entry.get("end_time"), "day_times.end_time")
        if err:
            return None, err
        if not parsed_start or not parsed_end:
            return None, "Each day_time requires start_time and end_time"
        if parsed_end <= parsed_start:
            return None, "day_times.end_time must be after day_times.start_time"
        day_times.append({"weekday": weekday[0], "start_time": parsed_start, "end_time": parsed_end})

    if schedule_type == "recurring" and not weekdays:
        return None, "weekdays is required for recurring schedules"

    if not default_start_time and not default_end_time and not day_times:
        return None, "Provide start_time/end_time or per-day day_times"

    if day_times:
        provided_days = {dt["weekday"] for dt in day_times}
        if weekdays and not provided_days.issubset(set(weekdays)):
            return None, "day_times.weekday must be within weekdays"
        if not weekdays:
            weekdays = sorted(provided_days)

    return (
        {
            "schedule_type": schedule_type,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": tz,
            "weekdays": weekdays,
            "default_start_time": default_start_time,
            "default_end_time": default_end_time,
            "day_times": day_times,
        },
        None,
    )


def _get_kids_for_enrollment(kid_ids: List[str], household_id: str) -> Tuple[Optional[List[Kid]], Optional[str]]:
    if not kid_ids:
        return None, "kid_ids is required"
    kids = Kid.query.filter(Kid.id.in_(kid_ids)).all()
    if len(kids) != len(set(kid_ids)):
        return None, "One or more kids not found"
    for kid in kids:
        if kid.household_id != household_id:
            return None, "All kids must belong to the current household"
    return kids, None


def _serialize_activity(activity: Activity) -> Dict[str, object]:
    schedule = activity.schedule
    day_times = []
    if schedule:
        if schedule.day_times:
            day_times = [
                {
                    "weekday": dt.weekday,
                    "start_time": _format_time(dt.start_time),
                    "end_time": _format_time(dt.end_time),
                }
                for dt in schedule.day_times
            ]
        elif schedule.recurrence_weekdays and schedule.default_start_time and schedule.default_end_time:
            day_times = [
                {
                    "weekday": w,
                    "start_time": _format_time(schedule.default_start_time),
                    "end_time": _format_time(schedule.default_end_time),
                }
                for w in schedule.recurrence_weekdays
            ]

    return {
        "id": activity.id,
        "name": activity.name,
        "provider": activity.provider,
        "address": activity.address,
        "location": activity.location,
        "latitude": activity.latitude,
        "longitude": activity.longitude,
        "household_id": activity.household_id,
        "created_by_user_id": activity.created_by_user_id,
        "kids": [
            {"id": e.kid.id, "first_name": e.kid.first_name if e.kid else None}
            for e in activity.enrollments
        ],
        "schedule": {
            "type": schedule.schedule_type if schedule else None,
            "start_date": schedule.start_date.isoformat() if schedule and schedule.start_date else None,
            "end_date": schedule.end_date.isoformat() if schedule and schedule.end_date else None,
            "timezone": schedule.timezone if schedule else None,
            "weekdays": schedule.recurrence_weekdays if schedule else [],
            "default_start_time": _format_time(schedule.default_start_time) if schedule else None,
            "default_end_time": _format_time(schedule.default_end_time) if schedule else None,
            "day_times": day_times,
        }
        if schedule
        else None,
        "created_at": activity.created_at.isoformat() if activity.created_at else None,
    }


@activity_bp.route("", methods=["POST"])
@auth_required
def create_activity():
    payload = request.get_json(silent=True) or {}
    current_user = getattr(g, "current_user", None)
    if not current_user or not getattr(current_user, "id", None):
        return error_response("User not found", status_code=401)
    household_id = getattr(current_user, "household_id", None)
    if not household_id:
        return error_response("User must belong to a household", status_code=400)

    name = (payload.get("name") or "").strip()
    if not name:
        return error_response("name is required", status_code=400)

    schedule_data, err = _validate_schedule(payload)
    if err:
        return error_response(err, status_code=400)

    kid_ids = payload.get("kid_ids") or []
    kids, err = _get_kids_for_enrollment(kid_ids, household_id)
    if err:
        return error_response(err, status_code=400 if "not found" not in err else 404)

    latitude, err = _parse_float(payload.get("latitude"), "latitude")
    if err:
        return error_response(err, status_code=400)
    longitude, err = _parse_float(payload.get("longitude"), "longitude")
    if err:
        return error_response(err, status_code=400)

    activity = Activity(
        household_id=household_id,
        created_by_user_id=current_user.id,
        provider=payload.get("provider"),
        name=name,
        address=payload.get("address"),
        location=payload.get("location"),
        latitude=latitude,
        longitude=longitude,
    )
    db.session.add(activity)
    db.session.flush()

    schedule = ActivitySchedule(
        activity_id=activity.id,
        schedule_type=schedule_data["schedule_type"],
        start_date=schedule_data["start_date"],
        end_date=schedule_data["end_date"],
        timezone=schedule_data["timezone"],
        default_start_time=schedule_data["default_start_time"],
        default_end_time=schedule_data["default_end_time"],
        recurrence_weekdays=schedule_data["weekdays"],
    )
    db.session.add(schedule)
    db.session.flush()

    for dt in schedule_data["day_times"]:
        db.session.add(
            ActivityDayTime(
                schedule_id=schedule.id,
                weekday=dt["weekday"],
                start_time=dt["start_time"],
                end_time=dt["end_time"],
            )
        )

    for kid in kids:
        db.session.add(KidActivityEnrollment(kid_id=kid.id, activity_id=activity.id))

    db.session.commit()

    db.session.refresh(activity)
    return json_response(_serialize_activity(activity), status_code=201)


def _get_activity_for_user(activity_id: str, household_id: str) -> Optional[Activity]:
    activity = Activity.query.filter_by(id=activity_id).first()
    if not activity:
        return None
    if activity.household_id != household_id:
        return None
    return activity


@activity_bp.route("/<activity_id>", methods=["GET"])
@auth_required
def get_activity(activity_id: str):
    current_user = getattr(g, "current_user", None)
    household_id = getattr(current_user, "household_id", None)
    if not household_id:
        return error_response("User must belong to a household", status_code=400)

    activity = _get_activity_for_user(activity_id, household_id)
    if not activity:
        return error_response("Activity not found", status_code=404)

    return json_response(_serialize_activity(activity))


@activity_bp.route("/<activity_id>", methods=["PATCH"])
@auth_required
def update_activity(activity_id: str):
    payload = request.get_json(silent=True) or {}
    current_user = getattr(g, "current_user", None)
    household_id = getattr(current_user, "household_id", None)
    if not household_id:
        return error_response("User must belong to a household", status_code=400)

    activity = _get_activity_for_user(activity_id, household_id)
    if not activity:
        return error_response("Activity not found", status_code=404)

    name = payload.get("name")
    if name is not None:
        name_clean = str(name).strip()
        if not name_clean:
            return error_response("name cannot be empty", status_code=400)
        activity.name = name_clean

    # Determine whether schedule updates are present
    schedule_keys = {"schedule_type", "start_date", "end_date", "timezone", "weekdays", "day_times", "start_time", "end_time"}
    if activity.schedule is None:
        return error_response("Activity schedule is missing", status_code=500)
    if any(key in payload for key in schedule_keys):
        existing_schedule = activity.schedule
        schedule_payload = {
            "schedule_type": payload.get("schedule_type", existing_schedule.schedule_type),
            "start_date": payload.get("start_date", existing_schedule.start_date.isoformat()),
            "end_date": payload.get("end_date", existing_schedule.end_date.isoformat()),
            "timezone": payload.get("timezone", existing_schedule.timezone),
            "weekdays": payload.get("weekdays", existing_schedule.recurrence_weekdays),
            "start_time": payload.get("start_time", _format_time(existing_schedule.default_start_time)),
            "end_time": payload.get("end_time", _format_time(existing_schedule.default_end_time)),
            "day_times": payload.get(
                "day_times",
                [
                    {
                        "weekday": dt.weekday,
                        "start_time": _format_time(dt.start_time),
                        "end_time": _format_time(dt.end_time),
                    }
                    for dt in existing_schedule.day_times
                ],
            ),
        }

        schedule_data, err = _validate_schedule(schedule_payload)
        if err:
            return error_response(err, status_code=400)

        activity.schedule.schedule_type = schedule_data["schedule_type"]
        activity.schedule.start_date = schedule_data["start_date"]
        activity.schedule.end_date = schedule_data["end_date"]
        activity.schedule.timezone = schedule_data["timezone"]
        activity.schedule.default_start_time = schedule_data["default_start_time"]
        activity.schedule.default_end_time = schedule_data["default_end_time"]
        activity.schedule.recurrence_weekdays = schedule_data["weekdays"]

        # Replace day times
        ActivityDayTime.query.filter_by(schedule_id=activity.schedule.id).delete()
        for dt in schedule_data["day_times"]:
            db.session.add(
                ActivityDayTime(
                    schedule_id=activity.schedule.id,
                    weekday=dt["weekday"],
                    start_time=dt["start_time"],
                    end_time=dt["end_time"],
                )
            )

    if "kid_ids" in payload:
        kid_ids = payload.get("kid_ids") or []
        kids, err = _get_kids_for_enrollment(kid_ids, household_id)
        if err:
            return error_response(err, status_code=400 if "not found" not in err else 404)
        KidActivityEnrollment.query.filter_by(activity_id=activity.id).delete()
        for kid in kids:
            db.session.add(KidActivityEnrollment(kid_id=kid.id, activity_id=activity.id))

    for field in ("provider", "address", "location"):
        if field in payload:
            setattr(activity, field, payload.get(field))

    if "latitude" in payload:
        latitude, err = _parse_float(payload.get("latitude"), "latitude")
        if err:
            return error_response(err, status_code=400)
        activity.latitude = latitude
    if "longitude" in payload:
        longitude, err = _parse_float(payload.get("longitude"), "longitude")
        if err:
            return error_response(err, status_code=400)
        activity.longitude = longitude

    db.session.commit()
    db.session.refresh(activity)
    return json_response(_serialize_activity(activity))

