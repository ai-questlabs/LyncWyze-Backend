from datetime import date
from typing import List, Optional

from models import Kid, db


def create_kid(
    *,
    first_name: str,
    household_id: Optional[str],
    parent_user_id: Optional[str],
    dob: Optional[date] = None,
    gender: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> Kid:
    kid = Kid(
        first_name=first_name,
        household_id=household_id,
        parent_user_id=parent_user_id,
        dob=dob,
        gender=gender,
        avatar_url=avatar_url,
    )
    db.session.add(kid)
    db.session.commit()
    return kid


def list_kids_for_user(household_id: Optional[str], parent_user_id: Optional[str]) -> List[Kid]:
    query = Kid.query
    if household_id:
        query = query.filter_by(household_id=household_id)
    elif parent_user_id:
        query = query.filter_by(parent_user_id=parent_user_id)
    return query.order_by(Kid.created_at.desc()).all()
