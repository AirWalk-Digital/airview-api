from pprint import pprint
import flask
from airview_api.services import (
    resource_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ResourceSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "resources",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/resources"),
    description="resources related resources",
)


@blp.route("/")
class Resources(MethodView):
    @blp.arguments(ResourceSchema)
    @blp.response(200, ResourceSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new resource
        Returns the newly created resource
        """
        try:
            app = resource_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))

    @blp.response(204, ResourceSchema)
    @blp.arguments(ResourceSchema)
    @blp.role(Roles.COMPLIANCE_READER)
    def put(self, data):
        """update the resource by its reference and applicationId"""
        application_id: str = flask.request.args.get("applicationId")
        resource_reference: str = flask.request.args.get("reference")
        data = resource_service.upsert(application_id, resource_reference, data)

        return data