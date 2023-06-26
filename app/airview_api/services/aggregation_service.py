from airview_api.database import db
from sqlalchemy import text
import itertools
from datetime import datetime
import json


def get_compliance_aggregation(application_id):
    query = """
select
  tc.id,
  e.name environment_name,
  s.name system_name,
  s.stage system_stage,
  tc.name technical_control_name,
  c.severity,
  c.name,
  c.id,
  r.id resource_id,
  r.reference resource_reference,
  mr.last_modified
from
  environment e
  inner join application_environment ae
    on ae.environment_id = e.id
  inner join application a
    on a.id = ae.application_id
  inner join resource r
    on r.application_environment_id = ae.id
  inner join monitored_resource mr
    on mr.resource_id = r.id
  inner join technical_control tc
    on tc.id = mr.technical_control_id
  inner join control c
    on c.id=tc.control_id
  inner join system s
    on s.id=tc.system_id
where
  a.id = :application_id
  and mr.monitoring_state='FLAGGED'
"""
    result = db.session.execute(text(query), {"application_id": application_id})

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
                "severity": str.lower(key[5]).replace("critical", "high"),
                "control_name": key[6],
                "control_id": key[7],
                "resources": res,
                "raised_date_time": last_modified,
                "tickets": [],
            }
        )

    return d
