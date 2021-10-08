from pprint import pprint

from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import ArgumentValidationError
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.models import (
    TechnicalControl,
    System,
    ApplicationTechnicalControl,
    MonitoredResource,
    MonitoredResourceState,
    TechnicalControlType,
    ControlStatusDetail,
    NamedUrl,
    TechnicalControlSeverity,
)
from airview_api.database import db


def persist(application_technical_control_id, reference, state):
    try:
        item = MonitoredResource.query.filter_by(
            application_technical_control_id=application_technical_control_id,
            reference=reference,
        ).first()
        if item is None:
            item = MonitoredResource(
                application_technical_control_id=application_technical_control_id,
                reference=reference,
                state=state,
                last_modified=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
            )
            db.session.add(item)
            db.session.commit()
            return
        parsed_state = MonitoredResourceState[state]
        if item.state != parsed_state:
            item.last_modified = datetime.now(timezone.utc)
        item.last_seen = datetime.utcnow()
        item.state = state

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return item
