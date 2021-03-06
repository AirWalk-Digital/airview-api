from flask import request
from flask.views import MethodView

from airview_api.blueprint import Blueprint, Roles
from airview_api.schemas import SearchResultSchema, SearchQueryArgsSchema
from airview_api.search import init_search_backend

blp = Blueprint(
    "search",
    __name__,
    url_prefix="/search",
    description="Search endpoint to query existing documents."
)


search_backend = init_search_backend()


@blp.route("/")
class Search(MethodView):
    @blp.response(200, SearchResultSchema(many=True))
    @blp.arguments(SearchQueryArgsSchema, location="query")
    @blp.role(Roles.CONTENT_READER)
    def get(self, args):
        """
        Searches matching terms in a configured search backend.
        """
        results = []
        if search_backend and args:
            results = search_backend.query(**args)
        return results
