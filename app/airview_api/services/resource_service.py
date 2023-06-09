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


def upsert(data: dict):

    if "id" in data:
        raise AirViewValidationException("Id is not expected when upserting a record")
    resource = Resource.query.filter_by(
        application_id=data['application_id'], reference=data['reference']
    ).first()
    if resource is None:
        resource = Resource(**data)
        resource.last_modified = datetime.utcnow()

    elif (
        resource.application_id != data["application_id"]
        or resource.service_id != data["service_id"]
        or resource.name != data["name"]
    ):
        resource.last_modified = datetime.utcnow()

    resource.last_seen = datetime.utcnow()
    resource.application_id = data["application_id"]
    resource.service_id = data["service_id"]
    resource.name = data["name"]

    try:
        db.session.add(resource)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")

    return resource


def get(application_id: str, reference: str):
    resource = Resource.query.filter_by(
        application_id=application_id, reference=reference
    ).first()
    if resource is None:
        raise AirViewNotFoundException
    return resource
