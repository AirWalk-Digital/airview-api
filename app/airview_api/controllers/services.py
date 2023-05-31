from pprint import pprint
import flask
from airview_api.services import (
    service_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import (
    ServiceSchema,
)
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "services",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/services"),
    description="services related resources",
)


@blp.route("/")
class Services(MethodView):
    @blp.arguments(ServiceSchema)
    @blp.response(200, ServiceSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """Create a new service
        Returns the newly created service
        """
        try:
            print(data)
            app = service_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))

    @blp.response(200, ServiceSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self):
        """Get a list of all services"""
        data = service_service.get_all()
        return data
