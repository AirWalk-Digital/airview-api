from pprint import pprint
import flask
from airview_api.services import (
    system_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    SystemSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "systems",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/systems"),
    description="systems related resources",
)


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
