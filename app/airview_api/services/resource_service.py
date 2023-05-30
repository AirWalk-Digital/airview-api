from airview_api.models import Resource
from airview_api.database import db
from airview_api.services import AirViewNotFoundException, AirViewValidationException
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    resource = Resource(**data)
    resource.last_seen = datetime.utcnow()
    resource.last_modified = datetime.utcnow()
    try:
        db.session.add(resource)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")

    return resource
