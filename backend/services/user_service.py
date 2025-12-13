from typing import Optional

from models import User, db


def get_or_create_user(firebase_uid: str, email: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if user:
        return user

    user = User(
        firebase_uid=firebase_uid,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    db.session.add(user)
    db.session.commit()
    return user
