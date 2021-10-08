from flask.views import MethodView
from airview_api.blueprint import Blueprint, Roles
from marshmallow.utils import pprint
from airview_api.services import AirViewValidationException, aggregation_service
from airview_api.schemas import ApplicationStatusSchema

blp = Blueprint(
    "application-statuses",
    __name__,
    url_prefix="/application-statuses",
    description="Application Status related resources",
)


@blp.route("/")
class ApplicationStatuses(MethodView):
    @blp.response(200, ApplicationStatusSchema(many=True))
    @blp.role(Roles.COMPLIANCE_READER)
    def get(self):
        """Get an aggregated overview of statuses for all applications"""
        data = aggregation_service.get_application_compliance_overview()
        return data
