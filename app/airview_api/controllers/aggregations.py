from itertools import compress
from pprint import pprint
from airview_api.blueprint import Blueprint, Roles
from airview_api.services import (
    aggregation_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
import flask
from flask import request

from airview_api.schemas import (
    ComplianceAggregationSchema,
    ControlOverviewResourceSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "aggregations",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/aggregations"),
    description="Aggregation based resources",
)


@blp.route("compliance/<int:application_id>")
class Application(MethodView):
    @blp.response(200, ComplianceAggregationSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_id):
        """Get an application by id

        Returns application matching requested id
        """
        return aggregation_service.get_compliance_aggregation(application_id)


@blp.route("control-overview-resources/<int:application_id>/")
class ControlOverviewResources(MethodView):
    @blp.response(200, ControlOverviewResourceSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_id):
        """Get an application by id
        Returns application matching requested id
        """
        technical_control_id: int = flask.request.args.get("technicalControlId")
        return aggregation_service.get_control_overview_resources(
            application_id, technical_control_id
        )
