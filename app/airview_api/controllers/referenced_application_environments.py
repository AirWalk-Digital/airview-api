from airview_api.services import (
    application_environment_service,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort

from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ApplicationEnvironmentReferenceSchema,
    ApplicationEnvironmentSchema,
    ApplicationSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "referenced-applications",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix(
        "/referenced-application-environments"
    ),
    description="Referenced App related resources",
)


@blp.route("/")
class Application(MethodView):
    @blp.arguments(ApplicationEnvironmentReferenceSchema, location="query")
    @blp.response(200, ApplicationEnvironmentSchema)
    @blp.role(Roles.CONTENT_READER)
    def get(self, args):
        """Get a refererenced application which matches the provided query params
        Returns the application definition matching the required params
        """
        try:
            data = application_environment_service.get_by_reference(**args)
            return data
        except AirViewNotFoundException:
            abort(404)
