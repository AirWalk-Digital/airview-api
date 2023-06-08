from airview_api.helpers import AirviewApiHelpers
from airview_api.schemas import ComplianceDataSchema
from airview_api.blueprint import Blueprint, Roles
from flask.views import MethodView
from flask import request
from flask_smorest import abort
from airview_api.services import AirViewValidationException

from airview_api.services import compliance_service

blp = Blueprint(
    "compliance",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/compliance"),
    description="compliance based resources",
)


@blp.route("/")
class ComplianceData(MethodView):
    @blp.response(200, ComplianceDataSchema(many=True))
    def get(self):
        """Get an application by id

        Returns application matching requested id
        """

        odata_filter = request.args.get("$filter")
        odata_select = request.args.get("$select")
        if not odata_select:
            abort(400, message="The $select query parameter must be passed")

        try:
            return compliance_service.get_compliace_aggregate(
                filter=odata_filter, select=odata_select
            )
        except AirViewValidationException as e:
            abort(400, message=str(e))
