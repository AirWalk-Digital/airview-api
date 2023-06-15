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


def get_by_application(application_id: int):
    return ApplicationEnvironment.query.filter_by(application_id=application_id)


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
    references = data.pop("references", [])
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
    references = [
        ApplicationEnvironmentReference(**r) for r in data.pop("references", [])
    ]
    try:
        app.environment_id = data["environment_id"]
        app.application_id = data["application_id"]

        # Get the existing reference values
        existing_references = app.references.all()

        # Remove any non-present references
        for r in existing_references:
            if not next(
                iter(
                    [
                        n
                        for n in references
                        if r.type == n.type and r.reference == n.reference
                    ]
                ),
                None,
            ):
                ApplicationEnvironmentReference.query.filter_by(id=r.id).delete()

        # Find the references to be added
        references_to_add = [
            ref for ref in references if ref not in existing_references
        ]

        # Add the new references
        app.references.extend(references_to_add)

        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        print(e)
        raise AirViewValidationException("Integrity Error, check reference fields")
