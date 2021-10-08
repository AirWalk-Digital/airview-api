from pprint import pprint

from datetime import datetime
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


def get_by_ids(application_id: int, technical_control_id: int):
    app = ApplicationTechnicalControl.query.filter_by(
        application_id=application_id, technical_control_id=technical_control_id
    ).first()
    return app


def create_with_ids(application_id: int, technical_control_id: int):
    try:
        atc = ApplicationTechnicalControl(
            application_id=application_id, technical_control_id=technical_control_id
        )
        db.session.add(atc)
        db.session.commit()
        return atc
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException()
