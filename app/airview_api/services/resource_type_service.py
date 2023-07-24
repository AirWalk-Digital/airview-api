from airview_api.models import ResourceType
from airview_api.database import db
from airview_api.services import AirViewNotFoundException, AirViewValidationException
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    resource_type = ResourceType(**data)
    try:
        db.session.add(resource_type)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")

    return resource_type


def get(reference: str):
    resource = ResourceType.query.filter_by(reference=reference).first()
    if resource is None:
        raise AirViewNotFoundException
    return resource
