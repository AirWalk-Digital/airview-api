from pprint import pprint
import flask
from airview_api.services import (
    resource_type_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ResourceTypeSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "resource-types",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/resource-types"),
    description="resources type related resources",
)


@blp.route("/")
class ResourceTypes(MethodView):
    @blp.arguments(ResourceTypeSchema)
    @blp.response(200, ResourceTypeSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new resource
        Returns the newly created resource
        """
        try:
            app = resource_type_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(409, message=str(e))

    @blp.response(200, ResourceTypeSchema)
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self):
        """update the resource by its reference and applicationId"""
        reference: str = flask.request.args.get("reference")
        try:
            data = resource_type_service.get(reference=reference)

            return data
        except AirViewNotFoundException:
            abort(404)
