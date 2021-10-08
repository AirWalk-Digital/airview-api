from airview_api.services import application_type_service, application_service
from airview_api.schemas import ApplicationSchema, IdAndNameSchema
from airview_api.blueprint import Blueprint, Roles
from flask.views import MethodView

blp = Blueprint(
    "application-types",
    __name__,
    url_prefix="/application-types",
    description="App type related resources",
)


@blp.route("/")
class ApplicationTypes(MethodView):
    @blp.response(200, IdAndNameSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self):
        """ "Get a list of all application types"""
        return application_type_service.get_all()


@blp.route("/<int:application_type_id>/applications/")
class Applications(MethodView):
    @blp.response(200, ApplicationSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_type_id):
        """Get a list of applications for the given application type"""
        return application_service.get_by_type(application_type_id)
