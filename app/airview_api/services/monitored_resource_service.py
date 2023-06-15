from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException
from airview_api.models import (
    MonitoredResource,
    MonitoredResourceState,
)
from airview_api.database import db


def persist(
    technical_control_id,
    resource_id,
    monitoring_state,
    additional_data="",
):
    try:
        item = MonitoredResource.query.filter_by(
            technical_control_id=technical_control_id, resource_id=resource_id
        ).first()
        if item is None:
            item = MonitoredResource(
                technical_control_id=technical_control_id,
                resource_id=resource_id,
                monitoring_state=monitoring_state,
                last_modified=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                additional_data=additional_data,
            )
            db.session.add(item)
            db.session.commit()
            return
        parsed_state = MonitoredResourceState[monitoring_state]
        if item.monitoring_state != parsed_state:
            item.last_modified = datetime.now(timezone.utc)
        item.last_seen = datetime.utcnow()
        item.monitoring_state = monitoring_state
        item.additional_data = additional_data

        db.session.commit()
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return item
