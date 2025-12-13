from typing import Optional

from models import Household, User, db


def create_household(*, name: str, address: Optional[str] = None, location: Optional[str] = None) -> Household:
    household = Household(name=name, address=address, location=location)
    db.session.add(household)
    db.session.commit()
    return household


def get_household_for_user(user: User) -> Optional[Household]:
    if not user or not getattr(user, "household_id", None):
        return None
    return Household.query.get(user.household_id)
