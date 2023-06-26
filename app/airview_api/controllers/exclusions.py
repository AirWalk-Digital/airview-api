from itertools import compress
from pprint import pprint
from airview_api.blueprint import Blueprint, Roles
from airview_api.services import (
    exclusion_service,
    AirViewValidationException,
    AirViewNotFoundException,
)
from flask.views import MethodView
from flask_smorest import abort
import flask
from flask import request

from airview_api.schemas import ExclusionSchema
from airview_api.helpers import AirviewApiHelpers


blp = Blueprint(
    "exclusions",
    __name__,
    url_prefix=AirviewApiHelpers.get_api_url_prefix("/exclusions"),
    description="exclusion based resources",
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
        except KeyError as e:
            print(e)
            abort(400, message="Bad Request")
        except AirViewValidationException:
            abort(400, message="Exclusions already exist for resources provided")
