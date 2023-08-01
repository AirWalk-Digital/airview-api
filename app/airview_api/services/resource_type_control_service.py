from airview_api.models import ResourceTypeControl
from airview_api.database import db
from airview_api.services import AirViewNotFoundException, AirViewValidationException
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app = ResourceTypeControl(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")

    return app


def get(control_id: int, resource_type_id: int):
    resource = ResourceTypeControl.query.filter_by(control_id=control_id, resource_type_id=resource_type_id).first()
    if resource is None:
        raise AirViewNotFoundException
    return resource
