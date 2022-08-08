from flask.views import MethodView
from flask_smorest import abort
from airview_api.services import (
    AirViewNotFoundException,
    exclusion_service,
    AirViewValidationException,
)
from airview_api.models import ExclusionState
from airview_api.schemas import ExclusionSchema
from airview_api.blueprint import Blueprint, Roles
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "exclusions",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/exclusions"),
    description="Exclusion related resources",
)


@blp.route("/")
class Exclusions(MethodView):
    @blp.arguments(ExclusionSchema)
    @blp.response(201)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Creates a new exclusion for the provided resources"""
        try:
            exclusion_service.create(
                data=data,
            )
        except KeyError:
            abort(400, message="Bad payload")
        except AirViewNotFoundException:
            abort(400, message="Appplication/Technical Control are not linked")
        except AirViewValidationException:
            abort(400, message="Exclusions already exist for resources provided")
