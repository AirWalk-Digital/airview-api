from airview_api.database import db
from sqlalchemy import func, literal
import itertools
from datetime import datetime
import json

from airview_api.models import (
    Application,
    Resource,
    MonitoredResource,
    TechnicalControl,
    MonitoredResourceState,
    Control,
    Environment,
    ApplicationEnvironment,
    System,
    QualityModel,
    Service,
)


def get_control_overviews(application_id: int, quality_model: str):
    qry = (
        db.select(
            TechnicalControl.id,
            TechnicalControl.name,
            TechnicalControl.control_action,
            Control.severity,
            System.name.label("system_name"),
            System.stage.label("system_stage"),
            literal(0).label("exempt"),
            func.count(TechnicalControl.id).label("applied"),
            # func.count(db.column("is_compliant")).label("total"),
        )
        .select_from(TechnicalControl)
        .join(Control)
        .join(System)
        .join(Service)
        .group_by(
            TechnicalControl.id,
            TechnicalControl.name,
            TechnicalControl.control_action,
            Control.severity,
            System.name,
            System.stage,
        )
        .limit(10)
    )
    result = db.session.execute(qry).all()
    print(result)
    return result


def get_application_quality_models(application_id):
    qry = (
        db.select(Control.quality_model)
        .select_from(ApplicationEnvironment)
        .join(Resource)
        .join(Service)
        .join(Control)
        .where(ApplicationEnvironment.application_id == application_id)
        .distinct()
    )

    result = db.session.execute(qry).all()
    mapped = [{"name": r[0].name} for r in result]
    return mapped


def get_compliance_aggregation(application_id):
    qry = (
        db.select(
            TechnicalControl.id,
            Environment.name,
            System.name,
            System.stage,
            TechnicalControl.name,
            Control.severity,
            Control.name,
            Control.id,
            Resource.id,
            Resource.reference,
            MonitoredResource.last_modified,
        )
        .select_from(Environment)
        .join(ApplicationEnvironment)
        .join(Resource)
        .join(MonitoredResource)
        .join(TechnicalControl)
        .join(Control)
        .join(System)
        .where(MonitoredResource.monitoring_state == MonitoredResourceState.FLAGGED)
        .where(Application.id == application_id)
    )

    result = db.session.execute(qry).all()

    key_func = lambda x: (x[:9])
    d = list()
    for key, group in itertools.groupby(result, key_func):
        m = None
        res = []
        # must be converted or results are inconsistant - https://stackoverflow.com/questions/39442128/itertools-groupby-function-seems-inconsistent
        list_group = list(group)
        last_modified = datetime.max
        for item in list_group:
            last_modified = item[10] if item[10] < last_modified else last_modified
            res = [{"id": g[8], "name": g[9], "status": "none"} for g in list_group]

        d.append(
            {
                "id": key[0],
                "environment_name": key[1],
                "system_name": key[2],
                "system_stage": key[3],
                "technical_control_name": key[4],
                "severity": str.lower(key[5].name).replace("critical", "high"),
                "control_name": key[6],
                "control_id": key[7],
                "resources": res,
                "raised_date_time": last_modified,
                "tickets": [],
            }
        )
    print(len(d))

    return d


def get_control_overview_resources(application_id, technical_control_id):
    qry = (
        db.select(
            Resource.id,
            Resource.reference,
            Environment.name.label("environment"),
            MonitoredResource.monitoring_state.label("status"),
            literal(False).label("pending"),
        )
        .select_from(ApplicationEnvironment)
        .join(Environment)
        .join(Resource)
        .join(Service)
        .join(Control)
        .join(TechnicalControl)
        .join(
            MonitoredResource,
            db.and_(
                TechnicalControl.id == MonitoredResource.technical_control_id,
                MonitoredResource.resource_id == Resource.id,
            ),
            isouter=True,
        )
        .where(ApplicationEnvironment.application_id == application_id)
        .where(TechnicalControl.id == technical_control_id)
    )
    print(qry)

    result = db.session.execute(qry).all()
    return result
