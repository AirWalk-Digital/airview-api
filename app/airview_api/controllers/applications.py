from itertools import compress
from pprint import pprint
from airview_api.blueprint import Blueprint, Roles
from airview_api.services import (
    application_service,
    aggregation_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
import flask

from airview_api.schemas import (
    ApplicationSchema,
    ControlOverviewResourceSchema,
    ControlStatusSchema,
    EnvironmentSchema,
    ControlOverviewSchema,
)

blp = Blueprint(
    "applications",
    __name__,
    url_prefix="/applications",
    description="Application based resources",
)


@blp.route("/<int:application_id>")
class Application(MethodView):
    @blp.response(200, ApplicationSchema)
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_id):
        """Get an application by id

        Returns application matching requested id
        """
        data = application_service.get_by_id(application_id)
        if data:
            return data

        abort(404)

    @blp.arguments(ApplicationSchema)
    @blp.response(204)
    @blp.role(Roles.CONTENT_WRITER)
    def put(self, data, application_id):
        """Update application definition matching provided id"""
        if application_id != data["id"]:
            abort(400, message="Id does not match payload")
        try:
            application_service.update(data)
        except AirViewNotFoundException:
            abort(404)
        except AirViewValidationException as e:
            abort(400, message=str(e))


@blp.route("/")
class Applications(MethodView):
    @blp.response(200, ApplicationSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self):
        """Get all applications"""
        return application_service.get_all()

    @blp.arguments(ApplicationSchema)
    @blp.response(200, ApplicationSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new application
        Returns the newly created application
        """
        try:
            app = application_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))


@blp.route("/<string:application_id>/environments")
class Environments(MethodView):
    @blp.response(200, EnvironmentSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_id):
        """Get all environments defined for this application
        Returns a list of applications
        """
        return application_service.get_environments(application_id)


@blp.route("/<int:application_id>/control-statuses")
class ControlStatuses(MethodView):
    @blp.response(200, ControlStatusSchema(many=True))
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self, application_id):
        """Get the current control statuses of resources/controls within this application"""
        return aggregation_service.get_control_statuses(application_id)


@blp.route("/<int:application_id>/control-overviews")
class ControlOverviews(MethodView):
    @blp.response(200, ControlOverviewSchema(many=True))
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self, application_id):
        quality_model = flask.request.args.get("qualityModel")
        """Get the current control statuses of resources/controls within this application"""
        data = aggregation_service.get_control_overviews(application_id, quality_model)
        return data


@blp.route("/<int:application_id>/monitored-resources")
class ControlOverviews(MethodView):
    @blp.response(200, ControlOverviewResourceSchema(many=True))
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self, application_id):
        technical_control_id = flask.request.args.get("technicalControlId")
        """Get the current control statuses of resources/controls within this application"""
        data = aggregation_service.get_control_overview_resources(
            application_id, technical_control_id
        )
        return data
