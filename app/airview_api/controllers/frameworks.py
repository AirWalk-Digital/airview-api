from flask import request
from flask.views import MethodView
from airview_api.blueprint import Blueprint, Roles
from airview_api.helpers import AirviewApiHelpers
from airview_api.services import (
    framework_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from airview_api.schemas import (
    FrameworkSchema,
    FrameworkSectionSchema,
    FrameworkControlObjectiveSchema
)
from flask_smorest import abort


blp = Blueprint(
    "frameworks",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/frameworks"),
    description="Framework based resources",
)


@blp.route("/")
class Frameworks(MethodView):
    @blp.response(200, FrameworkSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self):
        if request.args.get("name"):
            name = request.args['name']
            return framework_service.get_framework_by_name(name)
        return framework_service.get_all()

    @blp.arguments(FrameworkSchema)
    @blp.response(200, FrameworkSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data):
        try:
            app = framework_service.create_framework(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))


@blp.route("/<int:framework_id>")
class Framework(MethodView):
    @blp.response(200, FrameworkSchema)
    @blp.role(Roles.CONTENT_READER)
    def get(self, framework_id):
        data = framework_service.get_by_id(framework_id)
        return data


@blp.route("/<int:framework_id>/sections")
class FrameworkSection(MethodView):
    @blp.response(200, FrameworkSectionSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self,framework_id):
        if request.args.get("name"):
            name = request.args['name']
            return framework_service.get_framework_section_by_name(name)
        return framework_service.get_sections_by_framework(framework_id)

    
    @blp.arguments(FrameworkSectionSchema)
    @blp.response(200, FrameworkSectionSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data, framework_id):
        try:
            app = framework_service.create_framework_section(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))


@blp.route("/<int:framework_id>/sections/<int:section_id>/control_objectives")
class FrameworkControlObjective(MethodView):
    @blp.response(200, FrameworkControlObjectiveSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, framework_id, section_id):
        if request.args.get("name"):
            name = request.args['name']
            return framework_service.get_control_by_name(name)
        return framework_service.get_controls_by_framework_and_section(section_id)
    
    @blp.arguments(FrameworkControlObjectiveSchema)
    @blp.response(200, FrameworkControlObjectiveSchema)
    @blp.role(Roles.CONTENT_WRITER)
    def post(self, data, framework_id, section_id):
        try:
            app = framework_service.create_control_objective(data)
            return app
        except AirViewValidationException as e:
            abort(400, message=str(e))
