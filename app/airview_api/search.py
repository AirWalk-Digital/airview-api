import os

from typing import Optional

# Required
SEARCH_BACKEND = os.environ.get("SEARCH_BACKEND")

# Defaults
SEARCH_BACKEND_ELASTIC_SSL_ENABLED = bool(int(os.environ.get("SEARCH_BACKEND_ELASTIC_SSL_ENABLED", 1)))
SEARCH_BACKEND_ELASTIC_SSL_VERIFY_CERTS = bool(int(os.environ.get("SEARCH_BACKEND_ELASTIC_SSL_VERIFY_CERTS", 1)))
SEARCH_BACKEND_ELASTIC_PORT = os.environ.get("SEARCH_BACKEND_ELASTIC_PORT", "9200")


class SearchBackendNotDefinedError(Exception):
    """Raised when an unknown backend is configured."""


class SearchBackend:
    _client = None

    @property
    def client(self):
        if self._client is None:
            self.create_client()
        return self._client

    def create_client(self):
        raise NotImplementedError("create_client() must be implemented in child class.")

    def query(self, search_term: str):
        raise NotImplementedError("query() must be implemented in child class.")

    def serialize(self, data):
        raise NotImplementedError("serialize() must be implemented in child class.")


class ElasticsearchBackend(SearchBackend):
    def __init__(self, host: str, api_key: str, index: str, port: str = "9200"):
        super(ElasticsearchBackend, self).__init__()
        self.host = f"{host}:{port}"
        self.api_key = api_key
        self.index = index

    def create_client(self):
        from elasticsearch import Elasticsearch
        self._client = Elasticsearch(
            [self.host],
            api_key=self.api_key,
            use_ssl=SEARCH_BACKEND_ELASTIC_SSL_ENABLED,
            verify_certs=SEARCH_BACKEND_ELASTIC_SSL_VERIFY_CERTS
        )
        return self._client

    def serialize(self, data):
        output = []
        try:
            actual_data = data['hits']['hits']
            if isinstance(actual_data, list):
                for payload in actual_data:
                    sections = {
                        "summary": "\n".join(payload['highlight']['content']),
                        **payload['_source']
                    }
                    output.append(sections)
            elif isinstance(actual_data, dict):
                output = [{
                    "summary": "\n".join(actual_data['highlight']['content']),
                    **actual_data['_source']
                }]
        except KeyError:
            return []
        return output

    def query(self, q: str = None, limit: int = 20, context_size: int = 100):
        body = {
            "query": {
                # Returns a ranked search.
                "multi_match": {
                    "query": q
                }
            },
            # Returns context of the matched search
            "highlight": {
                "fragment_size": context_size,
                "order": "score",
                "pre_tags": [""],
                "post_tags": [""],
                "fields": {
                    "content": {}
                }
            }
        }


        results = []
        if q:
            search_result = self.client.search(
                index=self.index,
                body=body,
                filter_path=[
                    'hits.hits._source.path',
                    'hits.hits._source.title',
                    'hits.hits.highlight.content'
                ],
                size=limit
            )

            if search_result:
                results = self.serialize(search_result)

        return results


def init_search_backend() -> Optional[SearchBackend]:
    """Initialises a configured search backend."""
    backend = SEARCH_BACKEND.lower() if SEARCH_BACKEND else None
    if backend is None:
        return
    if backend == "elasticsearch":
        kwargs = {
            "api_key": os.environ['SEARCH_BACKEND_ELASTIC_API_TOKEN'],
            "host": os.environ['SEARCH_BACKEND_ELASTIC_HOST'],
            "port": SEARCH_BACKEND_ELASTIC_PORT,
            "index": os.environ['SEARCH_BACKEND_ELASTIC_INDEX']
        }
        return ElasticsearchBackend(**kwargs)
    else:
        raise SearchBackendNotDefinedError(f"Backend '{backend}' is not defined.")
