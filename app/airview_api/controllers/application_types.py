from airview_api.services import application_type_service, application_service, AirViewValidationException
from airview_api.schemas import ApplicationSchema, IdAndNameSchema
from airview_api.blueprint import Blueprint, Roles
from flask.views import MethodView
from flask_smorest import abort

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

    @blp.arguments(IdAndNameSchema)
    @blp.response(200, IdAndNameSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        """ Create a new application type
        Returns the newly created application
        """
        try:
            app = application_type_service.create(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))

""

@blp.route("/<int:application_type_id>/applications/")
class Applications(MethodView):
    @blp.response(200, ApplicationSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, application_type_id):
        """Get a list of applications for the given application type"""
        return application_service.get_by_type(application_type_id)
