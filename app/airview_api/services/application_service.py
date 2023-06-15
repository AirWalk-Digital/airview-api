from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.log import Identified
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.models import (
    Application,
    System,
    ApplicationType,
)
from airview_api.database import db
import itertools
from collections import defaultdict
import re


def get_all(application_type: str = None):
    if application_type is not None:
        return Application.query.filter_by(application_type=application_type)

    return Application.query.all()  #


def get_by_id(application_id: int):
    app = Application.query.get(application_id)
    return app


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app = Application(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except (IntegrityError, DataError) as e:
        print(e)

        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
    return app


def update(data: dict):
    app = Application.query.get(data["id"])
    if app is None:
        raise AirViewNotFoundException()
    app.name = data["name"]
    app.application_type = ApplicationType[data["application_type"]]
    try:
        db.session.commit()
    except (IntegrityError, DataError):
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
