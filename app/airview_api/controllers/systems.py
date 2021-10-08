from pprint import pprint
import flask
from airview_api.services import (
    technical_control_service,
    exclusion_service,
    application_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.models import ExclusionState
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ApplicationSchema,
    ExclusionResourceSchema,
    TechnicalControlSchema,
)


blp = Blueprint(
    "systems",
    __name__,
    url_prefix="/systems",
    description="systems related resources",
)


@blp.route("/<string:system_id>/exclusion-resources/")
class ExclusionResources(MethodView):
    @blp.response(200, ExclusionResourceSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, system_id):
        """Get a list of all exclusion resources for the given system, optionally filtered by type"""
        state_str = flask.request.args.get("state")

        try:
            state = ExclusionState[state_str] if state_str is not None else None
        except:
            return []

        resources = exclusion_service.get_by_system(system_id=system_id, state=state)
        return resources
