from airview_api.services import AirViewValidationException, technical_control_service
from airview_api.schemas import ControlStatusDetailSchema
from airview_api.blueprint import Blueprint, Roles
from flask.views import MethodView
from flask_smorest import abort

blp = Blueprint(
    "control-statuses",
    __name__,
    url_prefix="/control-statuses",
    description="Control Status related resources",
)


@blp.route("/<string:control_status_id>/control-status-detail")
class ControlStatusDetail(MethodView):
    @blp.response(200, ControlStatusDetailSchema)
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self, control_status_id):
        """Get the details of control status record by id"""
        data = technical_control_service.get_control_status_detail_by_id(
            control_status_id
        )

        return data
