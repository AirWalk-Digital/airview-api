from pprint import pprint

from datetime import datetime
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException
from airview_api.models import (
    Control,
)
from airview_api.database import db


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app = Control(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return app


def get_by_name(name: str):
    data = Control.query.filter_by(name=name)
    return data


def get_all():
    return Control.query.all()
