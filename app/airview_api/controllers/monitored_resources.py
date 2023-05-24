from pprint import pprint
import flask
from airview_api.services import (
    technical_control_service,
    exclusion_service,
    application_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.models import ExclusionState
import marshmallow as ma
from airview_api.schemas import CamelCaseSchema
from airview_api.services import monitored_resource_service
from airview_api.schemas import MonitoredResourceSchema
from airview_api.blueprint import Blueprint, Roles
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "monitored-resources",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/monitored-resources"),
    description="monitored-resources related resources",
)


@blp.route("/")
class MonitoredResource(MethodView):
    @blp.response(204)
    @blp.arguments(
        MonitoredResourceSchema(only=("application_technical_control_id", "resource_id")),
        location="query",
    )
    @blp.arguments(
        MonitoredResourceSchema(only=["monitoring_state", "additional_data"])
    )
    @blp.role(Roles.COMPLIANCE_WRITER)
    def put(self, args, data):
        """Persists the status of a monitored resource which is uniquely identified by the incoming query params"""
        try:
            data.update(args)
            monitored_resource_service.persist(**data)
        except AirViewNotFoundException:
            return "Not Found", 404
