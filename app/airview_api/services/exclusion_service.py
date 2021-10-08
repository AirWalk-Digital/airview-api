from pprint import pprint
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.models import (
    Exclusion,
    ApplicationTechnicalControl,
    ExclusionResource,
    ExclusionState,
    TechnicalControl,
    ApplicationReference,
    Application,
)
from airview_api.database import db


def get_by_system(system_id: int, state=None):
    filters = []
    results = (
        db.session.query(
            ExclusionResource.id,
            ExclusionResource.reference,
            ExclusionResource.state,
            TechnicalControl.reference,
            Application.id,
        )
        .join(Exclusion)
        .join(ApplicationTechnicalControl)
        .join(Application)
        .join(ApplicationReference)
        .join(TechnicalControl)
        .filter(TechnicalControl.system_id == system_id)
    )

    if state is not None:
        results = results.filter(ExclusionResource.state == state)

    mapped = [
        {
            "id": r[0],
            "reference": r[1],
            "state": r[2],
            "technical_control_reference": r[3],
            "application_references": ApplicationReference.query.filter_by(
                application_id=r[4]
            ).all(),
        }
        for r in results.all()
    ]
    return mapped


def create(data: dict):
    try:
        app_tech_control = ApplicationTechnicalControl.query.get(
            data["application_technical_control_id"]
        )
        if app_tech_control is None:
            raise AirViewNotFoundException()

        # To Do: Can this be done db side?
        existing_resources = []
        for e in app_tech_control.exclusions:
            for r in e.resources:
                existing_resources.append(r.reference)

        mapped = list()
        for r in data["resources"]:
            if r in existing_resources:
                raise AirViewValidationException("Exclusion exists for resource")
            mapped.append(ExclusionResource(reference=r, state=ExclusionState.PENDING))

        data["resources"] = mapped
        data["application_technical_control_id"] = app_tech_control.id
        exclusion = Exclusion(**data)

        db.session.add(exclusion)
        db.session.commit()

    except IntegrityError as e:
        print(e)
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")


def update(data: dict):
    app = ExclusionResource.query.get(data["id"])
    if app is None:
        raise AirViewNotFoundException()
    app.state = data["state"]

    db.session.commit()
