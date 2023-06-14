from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.log import Identified
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.models import (
    Application,
    System,
    ApplicationEnvironment,
    ApplicationEnvironmentReference,
    ApplicationType,
)
from airview_api.database import db
import itertools
from collections import defaultdict
import re


def get_by_id(application_environment_id: int):
    app = ApplicationEnvironment.query.get(application_environment_id)
    return app


def get_by_reference(type, reference):
    link = ApplicationEnvironmentReference.query.filter_by(
        type=type, reference=reference
    ).first()
    if link is None:
        raise AirViewNotFoundException()
    return link.application_environment


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app = ApplicationEnvironment(**data)
    try:
        for r in references:
            app.references.append(ApplicationEnvironmentReference(**r))

        db.session.add(app)
        db.session.commit()
    except (IntegrityError, DataError) as e:
        print(e)

        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
    return app


def update(data: dict):
    app = ApplicationEnvironment.query.get(data["id"])
    if app is None:
        raise AirViewNotFoundException()
    app.environment_id = data.get("environment_id")
    try:
        db.session.commit()
    except (IntegrityError, DataError):
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
