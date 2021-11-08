from airview_api.models import System
from airview_api.database import db
from airview_api.services import AirViewValidationException
from sqlalchemy.exc import IntegrityError


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    system = System(**data)
    try:
        db.session.add(system)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
        
    return system

