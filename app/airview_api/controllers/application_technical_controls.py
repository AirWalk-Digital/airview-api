from pprint import pprint
from flask import request
from airview_api.services import (
    AirViewValidationException,
    application_technical_control_service,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.models import ExclusionState
from airview_api.schemas import ApplicationTechnicalControlSchema


blp = Blueprint(
    "application-technical-controls",
    __name__,
    url_prefix="/application-technical-controls",
    description="application-technical-controls related resources",
)


@blp.route("/")
class Systems(MethodView):
    @blp.role(Roles.CONTENT_READER)
    @blp.response(204)
    @blp.response(200, ApplicationTechnicalControlSchema)
    @blp.arguments(
        ApplicationTechnicalControlSchema(
            only=["technical_control_id", "application_id"]
        ),
        location="query",
    )
    def get(self, args):
        """Get an existing linking record between an application and a technical control"""
        try:
            app = application_technical_control_service.get_by_ids(**args)
            if app is None:
                abort(404)
            return app

        except AirViewNotFoundException:
            abort(404)

    @blp.arguments(ApplicationTechnicalControlSchema)
    @blp.response(200, ApplicationTechnicalControlSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new linkage between an application and a technical control
        Returns the newly created definition
        """
        try:
            app = application_technical_control_service.create_with_ids(**data)
            return app
        except AirViewValidationException:
            abort(409)
