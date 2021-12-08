from pprint import pprint
import flask
from airview_api.services import (
    technical_control_service,
    exclusion_service,
    system_service,
    application_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.models import ExclusionState
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ApplicationSchema,
    ExclusionResourceSchema,
    SystemSchema,
    TechnicalControlSchema,
)


blp = Blueprint(
    "systems",
    __name__,
    url_prefix="/systems",
    description="systems related resources",
)


@blp.route("/<string:system_id>/exclusion-resources/")
class ExclusionResources(MethodView):
    @blp.response(200, ExclusionResourceSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, system_id):
        """Get a list of all exclusion resources for the given system, optionally filtered by type"""
        state_str = flask.request.args.get("state")

        try:
            state = ExclusionState[state_str] if state_str is not None else None
        except:
            return []

        resources = exclusion_service.get_by_system(system_id=system_id, state=state)
        return resources


@blp.route("/")
class Systems(MethodView):
    @blp.arguments(SystemSchema)
    @blp.response(200, SystemSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new system
        Returns the newly created system
        """
        try:
            app = system_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))

    @blp.response(200, SystemSchema())
    @blp.arguments(SystemSchema(only=("name",)), location="query")
    @blp.role(Roles.CONTENT_READER)
    def get(self, args):
        """Get a list of all technical controls"""
        try:
            data = system_service.get_by_name(**args)
            return data

        except AirViewNotFoundException:
            abort(404)
