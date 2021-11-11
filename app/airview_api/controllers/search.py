from flask.views import MethodView
from airview_api.blueprint import Blueprint, Roles
from airview_api.search import init_search_backend
from airview_api.schemas import SearchResultSchema


blp = Blueprint(
    "search",
    __name__,
    url_prefix="/search",
    description="Search endpoint to query existing documents."
)


search_backend = init_search_backend()


@blp.route("/<string:search_terms>")
class Search(MethodView):
    @blp.response(200, SearchResultSchema(many=True))
    @blp.role(Roles.CONTENT_READER)
    def get(self, search_terms):
        """
        Searches matching terms in a configured search backend.
        """
        results = []
        if search_backend:
            results = search_backend.query(search_terms)
        return results
