from datetime import datetime
from pprint import pprint
from sqlalchemy import func


from airview_api.services import AirViewValidationException
from airview_api.models import MonitoredResource
from airview_api.database import db


def get_control_status_by_id(control_status_id: int):
    triggered_resource = MonitoredResource.query.get(control_status_id)

    return {
        "id": control_status_id,
        "applicationServiceName": triggered_resource.application_service_technical_control.application_service.name,
        "control": {"name": "Ctrl 1", "url": "http://ccc"},
        "frameworks": [],
        "assignmentGroup": None,
        "assignee": None,
    }
