from airview_api.models import System
from airview_api.database import db
from airview_api.services import AirViewValidationException


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    system = System(**data)
    db.session.add(system)
    db.session.commit()
    return system

