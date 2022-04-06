from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException
from airview_api.models import (
    MonitoredResource,
    MonitoredResourceState,
)
from airview_api.database import db


def persist(application_technical_control_id, reference, monitoring_state, type):
    try:
        item = MonitoredResource.query.filter_by(
            application_technical_control_id=application_technical_control_id,
            reference=reference,
        ).first()
        if item is None:
            item = MonitoredResource(
                application_technical_control_id=application_technical_control_id,
                reference=reference,
                monitoring_state=monitoring_state,
                last_modified=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                type=type,
            )
            db.session.add(item)
            db.session.commit()
            return
        parsed_state = MonitoredResourceState[monitoring_state]
        if item.monitoring_state != parsed_state:
            item.last_modified = datetime.now(timezone.utc)
        item.last_seen = datetime.utcnow()
        item.monitoring_state = monitoring_state

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return item
