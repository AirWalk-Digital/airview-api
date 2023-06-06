from airview_api.helpers import AirviewApiHelpers
from odata_query.sqlalchemy import apply_odata_query
from airview_api.models import (
    Application,
    Resource,
    MonitoredResource,
    TechnicalControl,
    MonitoredResourceState,
)
from airview_api.database import db
from airview_api.blueprint import Blueprint, Roles
from flask.views import MethodView
import json
from sqlalchemy import text
from sqlalchemy import case


blp = Blueprint(
    "compliance",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/compliance"),
    description="compliance based resources",
)


@blp.route("/")
class ComplianceData(MethodView):
    def get(self):
        """Get an application by id

        Returns application matching requested id
        """

        # orm_query = db.select(models.Application)  # db.session.query(Application)
        # orm_query = db.select(models.Application.name, models.Resource.reference).join(
        # models.Application, models.Resource
        # )

        orm_query = db.select(
            Application.id.label("application_id"),
            Application.name.label("application_name"),
            Resource.reference.label("resource_reference"),
            TechnicalControl.reference.label("technical_control_reference"),
            case(
                [
                    (
                        MonitoredResource.monitoring_state
                        == MonitoredResourceState.MONITORING,
                        1,
                    )
                ],
                else_=0,
            ).label("isCompliant"),
        )

        odata_query = "name eq 'sub-awr-airview-001'"  # This will usually come from a query string parameter.

        query = apply_odata_query(orm_query, odata_query)
        results = db.session.execute(query).all()

        return json.dumps(
            [dict(r) for r in results], sort_keys=True, indent=4, separators=(",", ": ")
        )
