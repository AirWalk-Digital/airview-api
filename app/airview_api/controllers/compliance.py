from requests import request
from airview_api.helpers import AirviewApiHelpers
from odata_query.sqlalchemy import apply_odata_query
from airview_api.models import (
    Application,
    Resource,
    MonitoredResource,
    TechnicalControl,
    MonitoredResourceState,
)
from airview_api.schemas import ComplianceDataSchema
from airview_api.database import db
from airview_api.blueprint import Blueprint, Roles
from flask.views import MethodView
import json
from sqlalchemy import func, case
from sqlalchemy.sql.expression import cte
from flask import request


blp = Blueprint(
    "compliance",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/compliance"),
    description="compliance based resources",
)


@blp.route("/")
class ComplianceData(MethodView):
    @blp.response(200, ComplianceDataSchema(many=True))
    def get(self):
        """Get an application by id

        Returns application matching requested id
        """

        orm_query = (
            db.select(
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
            .select_from(TechnicalControl)
            .join(MonitoredResource)
            .join(Resource)
            .join(Application)
        )

        print(type(orm_query))
        # odata_query = "name eq 'sub-awr-airview-001'"  # This will usually come from a query string parameter.
        odata_filter = request.args.get("$filter")
        odata_select = request.args.get("$select")

        query = apply_odata_query(orm_query, odata_filter)

        splits = odata_select.split(",")
        print(splits)

        n = (
            db.select(
                # db.column("application_id"),
                [db.column(c) for c in splits]
                + [
                    func.sum(db.column("isCompliant")).label("isCompliant"),
                    func.count(db.column("isCompliant")).label("total"),
                ]
            ).select_from(query)
            # .group_by(db.column("application_id"))
            .group_by(db.text(odata_select))
            # .group_by([db.column(c) for c in odata_select.split(",")]),
        )

        results = db.session.execute(n).all()
        print(type(results[0][0]))
        print(results[0][0])

        return results
