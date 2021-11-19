from airview_api.models import (
    MonitoredResource,
    ExclusionState,
)
from airview_api.database import db
import itertools


def get_control_overviews(application_id: int, quality_model: str):
    sql = """
with recursive apps as (
  select application.id top_level_id, id from application where id=:application_id
  union all
  select apps.top_level_id, application.id from application join apps on apps.id = application.parent_id
)  
select
  tc.id, 
  tc.name,
  tc.control_type control_type,
  tc.severity,
  s.name system_name,
  s.stage system_stage,
  sum(cast(mr.exclusion_id is not null and mr.exclusion_state = 'ACTIVE' as int)) exempt,
  count(1) applied
from
  apps a
  join application_technical_control as atc
    on atc.application_id = a.id
  join technical_control tc
    on tc.id = atc.technical_control_id
  join monitored_resource mr
    on mr.application_technical_control_id=atc.id
  join system s
    on s.id = tc.system_id
group by
  tc.id,
  tc.name,
  tc.control_type,
  tc.severity,
  s.name,
  s.stage
  
  
    """
    result = db.session.execute(sql, {"application_id": application_id})
    data = [dict(r) for r in result]
    print(data)
    return data


def get_application_compliance_overview():
    sql = """
with recursive apps as (
  select application.id top_level_id, id from application where parent_id is null
  union all
  select apps.top_level_id, application.id from application join apps on apps.id = application.parent_id

),
current as(
  select
    t1.id,
    t1.top_level_id
  from (
    select
      tr.id,
      a.top_level_id,
      tr.state
    from
      monitored_resource tr
      join application_technical_control as atc
        on atc.id = tr.application_technical_control_id
      join apps a
        on a.id = atc.application_id
  ) as t1
)

select
  pa.id,
  pa.name application_name,
  e.name environment,
  sum(case when tc.severity = 'HIGH' and tr.state='FLAGGED' and tr.exclusion_id is null then 1 else 0 end) high,
  sum(case when tc.severity = 'MEDIUM' and tr.state='FLAGGED' and tr.exclusion_id is null then 1 else 0 end) medium,
  sum(case when tc.severity = 'LOW' and tr.state='FLAGGED' and tr.exclusion_id is null then 1 else 0 end) low,
  count(distinct(atc2.technical_control_id)) exempt_controls, 
  count(distinct case when tr.state='FLAGGED' and tr.exclusion_id is null then tc.id else null end) failed_controls,
  count(distinct tc.id) total_controls
from
  current c
  join monitored_resource tr
    on tr.id=c.id
  join application_technical_control as atc
    on atc.id = tr.application_technical_control_id
  join technical_control tc
    on tc.id = atc.technical_control_id
  join application a
    on a.id = atc.application_id
  left join environment e
    on e.id = a.environment_id
    join application pa
    on pa.id = c.top_level_id
  left join exclusion x
    on x.id = tr.exclusion_id
    and tr.exclusion_state = 'ACTIVE'
  left join application_technical_control atc2
    on atc2.id = x.application_technical_control_id 
group by
  pa.id,
  pa.name,
  e.name
order by
  pa.name
"""
    result = db.session.execute(sql)
    data = [dict(r) for r in result]
    key_func = lambda x: (x["id"], x["application_name"])

    return [
        {"id": key[0], "application_name": key[1], "environments": list(group)}
        for key, group in itertools.groupby(data, key_func)
    ]


def get_control_statuses(application_id: str):

    sql = """
with recursive apps as (
  select application.id from application where id=:application_id
  union all
  select application.id from application join apps on apps.id = application.parent_id

)
select
  atc.id,
  tc.name,
  tr.id triggered_resource_id,
  tr.reference triggered_resource_reference,
  tr.exclusion_state, 
  tr.last_modified logged_datetime,
  tc.severity,
  e.abbreviation environment,
  a.name application_name,
  tr.application_technical_control_id,
  s.name system_name,
  s.stage system_stage
from
  monitored_resource tr
  join application_technical_control as atc
    on atc.id=tr.application_technical_control_id
  join apps fa
    on fa.id = atc.application_id
  join technical_control tc
    on tc.id = atc.technical_control_id
  join system s
    on s.id = tc.system_id
  join application a
    on a.id = atc.application_id
  left join environment e
    on e.id = a.environment_id
  left join exclusion x
    on x.id = tr.exclusion_id
    and tr.exclusion_state='ACTIVE'
where
  tr.state = 'FLAGGED'
  -- and coalesce(x.state,'NONE') != 'ACTIVE'
order by
  tc.name,
  tc.severity
"""
    result = db.session.execute(sql, {"application_id": application_id})
    data = [dict(r) for r in result if r["exclusion_state"] != "ACTIVE"]

    key_func = lambda x: (
        x["id"],
        x["name"],
        x["severity"],
        x["environment"],
        x["application_name"],
        x["system_name"],
        x["system_stage"],
    )
    d = list()
    for key, group in itertools.groupby(data, key_func):
        m = None
        res = []
        # must be converted or results are inconsistant - https://stackoverflow.com/questions/39442128/itertools-groupby-function-seems-inconsistent
        list_group = list(group)
        for item in list_group:
            m = m or item
            m = item if item["logged_datetime"] < m["logged_datetime"] else m
            res = [
                {
                    "id": g["triggered_resource_id"],
                    "name": g["triggered_resource_reference"],
                    "state": g.get("exclusion_state") or ExclusionState.NONE,
                }
                for g in list_group
            ]

        mr = MonitoredResource.query.get(m["triggered_resource_id"])
        x = {
            "id": key[0],
            "controlType": "security",
            "severity": key[2].lower(),
            "name": key[1],
            "environment": key[3],
            "application": key[4],
            "systemName": key[5],
            "systemStage": key[6],
            "resources": res,
            "raisedDateTime": mr.last_modified,
            "tickets": [],
        }
        d.append(x)

    return d
