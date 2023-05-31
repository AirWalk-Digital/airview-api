from airview_api.services import technical_control_service, AirViewValidationException
from flask.views import MethodView
from flask_smorest import abort
from flask import request

from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    TechnicalControlSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "technical-controls",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/technical-controls"),
    description="Technical Control related resources",
)


@blp.route("/")
class TechnicalControls(MethodView):
    @blp.arguments(TechnicalControlSchema)
    @blp.response(200, TechnicalControlSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create new control"""
        try:
            control = technical_control_service.create(data)
            return control
        except AirViewValidationException as e:
            abort(400, message=str(e))

    @blp.response(200, TechnicalControlSchema(many=True))
    @blp.arguments(
        TechnicalControlSchema(only=("system_id", "reference")), location="query"
    )
    @blp.role(Roles.CONTENT_READER)
    def get(self, args):
        """Get a list of all technical controls"""
        data = technical_control_service.get_with_filter(**args)

        return data


@blp.route("/<string:control_id>")
class TechnicalControl(MethodView):
    @blp.response(200, TechnicalControlSchema)
    @blp.role(Roles.CONTENT_READER)
    def get(self, control_id):
        """Get single control"""
        data = technical_control_service.get_by_id(control_id)
        if data:
            return data
        abort(404)
