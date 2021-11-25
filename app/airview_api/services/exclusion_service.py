from pprint import pprint
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.models import (
    Exclusion,
    ApplicationTechnicalControl,
    MonitoredResource,
    ExclusionState,
    TechnicalControl,
    ApplicationReference,
    Application,
    MonitoredResourceState,
)
from airview_api.database import db
from sqlalchemy import and_


def get_by_system(system_id: int, state=None):
    filters = []
    results = (
        db.session.query(
            MonitoredResource.id,
            MonitoredResource.reference,
            MonitoredResource.exclusion_state,
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
        results = results.filter(MonitoredResource.exclusion_state == state)

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

        resources = MonitoredResource.query.filter(
            and_(
                ApplicationTechnicalControl.id == app_tech_control.id,
                MonitoredResource.reference.in_(data["resources"]),
            )
        ).all()

        data["application_technical_control_id"] = app_tech_control.id
        payload_resources = data["resources"]
        del data["resources"]
        exclusion = Exclusion(**data)
        for r in payload_resources:
            existing = next((x for x in resources if x.reference == r), None)
            # Update existing resources
            if existing:
                # It is not allowed to have a resource with multiple exclusions or to overwrite existing ones
                if existing.exclusion_id is not None:
                    raise AirViewValidationException("Exclusion exists for resource")
                existing.exclusion = exclusion
                existing.exclusion_state = ExclusionState.PENDING
            # Else create a new one
            else:
                exclusion.resources.append(
                    MonitoredResource(
                        reference=r,
                        state=MonitoredResourceState.FIXED_AUTO,
                        last_modified=datetime.now(timezone.utc),
                        application_technical_control_id=app_tech_control.id,
                        exclusion_state=ExclusionState.PENDING,
                    )
                )

        db.session.add(exclusion)

        # # To Do: Can this be done db side?
        # existing_resources = []
        # for e in app_tech_control.exclusions:
        #     for r in e.resources:
        #         existing_resources.append(r.reference)

        # mapped = list()
        # for r in data["resources"]:
        #     if r in existing_resources:
        #         raise AirViewValidationException("Exclusion exists for resource")
        #     mapped.append(ExclusionResource(reference=r, state=ExclusionState.PENDING))

        db.session.commit()

    except IntegrityError as e:
        print(e)
        print("here")
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")


def update(data: dict):
    app = MonitoredResource.query.get(data["id"])
    if app is None:
        raise AirViewNotFoundException()
    app.exclusion_state = data["state"]

    db.session.commit()
