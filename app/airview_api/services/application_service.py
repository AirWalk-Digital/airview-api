from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.log import Identified
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.models import (
    Application,
    System,
    ApplicationReference,
    ApplicationType,
)
from airview_api.database import db
import itertools
from collections import defaultdict
import re


def get_all(application_type: None):

    results = db.session.query(Application)
    if application_type is not None:
        results = results.filter(application_type == application_type)


def get_by_id(application_id: int):
    app = Application.query.get(application_id)
    return app


def get_by_reference(type, reference):
    link = ApplicationReference.query.filter_by(type=type, reference=reference).first()
    if link is None:
        raise AirViewNotFoundException()
    return link.application


def get_by_type(application_type: str):
    return Application.query.filter_by(
        application_type=ApplicationType[application_type]
    ).all()


def get_environments(application_id: int):
    # to do: Is there a more efficient way to do this?
    app = Application.query.get(application_id)
    if app is None:
        return []
    envs = {svc.environment for svc in app.children}
    if app.environment:
        envs.union({app.environment})
    return list(envs)


def _generate_unique_reference(name: str) -> str:
    ref = re.sub("[^0-9a-zA-Z]+", "_", name).lower()
    i = 0
    new_ref = ref
    while True:
        app = ApplicationReference.query.filter_by(
            type="_internal_reference", reference=new_ref
        ).first()
        if app is None:
            return new_ref
        new_ref = ref + "_" + str(i)
        if i >= 9:
            raise AirViewValidationException(
                "Cannot generate unique name. Too many duplicates"
            )
        i += 1


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    references = data.pop("references", [])
    app = Application(**data)
    references.insert(
        0,
        {
            "type": "_internal_reference",
            "reference": _generate_unique_reference(app.name),
        },
    )
    try:
        for r in references:
            app.references.append(ApplicationReference(**r))

        db.session.add(app)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
    return app


def update(data: dict):
    app = Application.query.get(data["id"])
    if app is None:
        raise AirViewNotFoundException()
    app.name = data["name"]
    app.application_type = ApplicationType[data["application_type"]]
    app.parent_id = data.get("parent_id")
    app.environment_id = data.get("environment_id")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
