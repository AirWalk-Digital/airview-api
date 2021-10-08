from flask.views import MethodView
from flask_smorest import abort
from airview_api.services import AirViewNotFoundException, exclusion_service
from airview_api.models import ExclusionState
from airview_api.schemas import ExclusionResourceSchema
from airview_api.blueprint import Blueprint, Roles

blp = Blueprint(
    "exclusion-resources",
    __name__,
    url_prefix="/exclusion-resources",
    description="Exclusion Resources related resources",
)


@blp.route("/<int:id>/")
class ExclusionResource(MethodView):
    @blp.arguments(ExclusionResourceSchema)
    @blp.response(204)
    @blp.role(Roles.COMPLIANCE_WRITER)
    def put(self, data, id):
        """Update the state of a specific exclusion resource"""
        try:
            if id != data["id"]:
                abort(400, message="Id does not match payload")
            state_str = data["state"]
            data["state"] = ExclusionState[state_str] if state_str is not None else None

            exclusion_service.update(data)

            return "No Content", 204
        except AirViewNotFoundException:
            return "Conflict", 409
