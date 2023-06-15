from itertools import compress
from pprint import pprint
from airview_api.blueprint import Blueprint, Roles
from airview_api.services import (
    application_environment_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
import flask
from flask import request

from airview_api.schemas import (
    ApplicationEnvironmentSchema,
    ApplicationSchema,
    ControlOverviewResourceSchema,
    ControlStatusSchema,
    EnvironmentSchema,
    ControlOverviewSchema,
    QualityModelSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "application-environments",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/application-environments"),
    description="Application Environment based resources",
)


@blp.route("/<int:application_environment_id>")
class Application(MethodView):
    @blp.response(200, ApplicationEnvironmentSchema)
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_environment_id):
        """Get an application environment by id

        Returns application environment matching requested id
        """
        data = application_environment_service.get_by_id(application_environment_id)
        if data:
            return data

        abort(404)

    @blp.arguments(ApplicationEnvironmentSchema)
    @blp.response(204)
    @blp.role(Roles.CONTENT_WRITER)
    def put(self, data, application_environment_id):
        """Update application definition matching provided id"""
        if application_environment_id != data["id"]:
            abort(400, message="Id does not match payload")
        try:
            application_environment_service.update(data)
        except AirViewNotFoundException:
            abort(404)
        except AirViewValidationException as e:
            abort(400, message=str(e))


@blp.route("/")
class ApplicationEnvironments(MethodView):
    @blp.arguments(ApplicationEnvironmentSchema)
    @blp.response(200, ApplicationEnvironmentSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new application environment
        Returns the newly created application environment
        """
        try:
            app = application_environment_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))
