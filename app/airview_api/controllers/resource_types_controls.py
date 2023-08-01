from pprint import pprint
import flask
from airview_api.services import (
    resource_type_control_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import ResourceTypeControlSchema
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "resource-types-controls",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/resource-types-controls"),
    description="resources type control relations",
)


@blp.route("/")
class ResourceTypeControl(MethodView):
    @blp.arguments(ResourceTypeControlSchema)
    @blp.response(200, ResourceTypeControlSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new resource
        Returns the newly created resource
        """
        try:
            app = resource_type_control_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(409, message=str(e))

    @blp.response(200, ResourceTypeControlSchema)
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self):
        """update the resource by its reference and applicationId"""
        control_id: int = flask.request.args.get("controlId")
        resource_type_id: int = flask.request.args.get("resourceTypeId")
        try:
            data = resource_type_control_service.get(control_id=control_id, resource_type_id=resource_type_id)

            return data
        except AirViewNotFoundException:
            abort(404)
