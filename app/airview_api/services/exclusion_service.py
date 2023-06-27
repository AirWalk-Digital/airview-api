from airview_api.database import db
from sqlalchemy import text
import itertools
from datetime import datetime
import json
from sqlalchemy.exc import IntegrityError
from airview_api.models import (
    Control,
    Resource,
    ExclusionResource,
    Exclusion,
    ExclusionState,
)
from airview_api.services import AirViewValidationException, AirViewNotFoundException


def create(data: dict):
    try:
        control = Control.query.get(data["control_id"])
        if control is None:
            raise AirViewNotFoundException()

        # To Do: Can this be done db side?
        existing_resources = []
        for e in control.exclusions:
            for r in e.resources:
                existing_resources.append(r.id)

        # exclusion = Exclusion(**data)
        exclusion = Exclusion()
        exclusion.control_id = data["control_id"]
        exclusion.summary = data["summary"]
        exclusion.notes = data["notes"]
        exclusion.is_limited_exclusion = data["is_limited_exclusion"]
        exclusion.end_date = datetime.max
        # mapped = list()
        for r in data["resources"]:
            if r in existing_resources:
                raise AirViewValidationException("Exclusion exists for resource")
            res = Resource.query.get(r)
            exclusion.resources.append(res)

        db.session.add(exclusion)
        db.session.commit()

    except IntegrityError as e:
        print(e)
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
