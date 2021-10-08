from airview_api.services import application_service, AirViewNotFoundException
from flask.views import MethodView
from flask_smorest import abort

from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ApplicationReferenceSchema,
    ApplicationSchema,
)

blp = Blueprint(
    "referenced-applications",
    __name__,
    url_prefix="/referenced-applications",
    description="Referenced App related resources",
)


@blp.route("/")
class Application(MethodView):
    @blp.arguments(ApplicationReferenceSchema, location="query")
    @blp.response(200, ApplicationSchema)
    @blp.role(Roles.CONTENT_READER)
    def get(self, args):
        """Get a refererenced application which matches the provided query params
        Returns the application definition matching the required params
        """
        try:
            data = application_service.get_by_reference(**args)
            return data
        except AirViewNotFoundException:
            abort(404)
