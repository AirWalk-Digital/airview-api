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


def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    data["severity"] = data.get("severity", TechnicalControlSeverity.HIGH)
    app = TechnicalControl(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return app


def get_by_id(application_id: int):
    app = TechnicalControl.query.get(application_id)
    return app


def get_with_filter(system_id: int = None, reference: str = None):
    results = db.session.query(TechnicalControl)
    if system_id is not None:
        results = results.filter(TechnicalControl.system_id == system_id)
    if reference is not None:
        results = results.filter(TechnicalControl.reference == reference)
    return results.all()


def get_control_status_detail_by_id(technical_control_id: int):
    triggered_resource = MonitoredResource.query.get(technical_control_id)

    return ControlStatusDetail(
        id=technical_control_id,
        application_name=triggered_resource.application_technical_control.application.name,
        control=NamedUrl(
            name=triggered_resource.application_technical_control.technical_control.name,
            url=None,
        ),
        frameworks=[],
        assignment_group=None,
        assignee=None,
    )
