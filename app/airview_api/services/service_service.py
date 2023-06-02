from airview_api.models import Service
from airview_api.database import db
from airview_api.services import AirViewNotFoundException, AirViewValidationException
from sqlalchemy.exc import IntegrityError


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    service = Service(**data)
    try:
        db.session.add(service)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")

    return service


def get_all():
    return Service.query.all()
