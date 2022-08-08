from airview_api.services import (
    environment_service,
    AirViewValidationException,
)
from airview_api.schemas import EnvironmentSchema
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "environments",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/environments"),
    description="Environment related resources",
)


@blp.route("/")
class Environments(MethodView):
    @blp.response(200, EnvironmentSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self):
        """Get a list of all environments"""
        return environment_service.get_all()

    @blp.arguments(EnvironmentSchema)
    @blp.response(200, EnvironmentSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create an new environment
        Returns newly created environment
        """
        try:
            app = environment_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))
