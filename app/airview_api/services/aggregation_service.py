from airview_api.database import db
from sqlalchemy import text
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
)


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
