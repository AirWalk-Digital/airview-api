from airview_api.services import control_service, AirViewValidationException
from flask.views import MethodView
from flask_smorest import abort
from flask import request

from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ControlSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "controls",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/controls"),
    description="Control related resources",
)


@blp.route("/")
class Controls(MethodView):
    @blp.arguments(ControlSchema)
    @blp.response(200, ControlSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create new control"""
        try:
            control = control_service.create(data)
            return control
        except AirViewValidationException as e:
            abort(400, message=str(e))

    @blp.response(200, ControlSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self):
        """Get a list of all controls"""
        if request.args.get("name"):
            name = request.args['name']
            return control_service.get_by_name(name)
        return control_service.get_all()
