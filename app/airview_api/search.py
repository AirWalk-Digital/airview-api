import os


# Required
SEARCH_BACKEND = os.environ.get("SEARCH_BACKEND")

# Defaults
SEARCH_BACKEND_ELASTIC_SSL_ENABLED = bool(int(os.environ.get("SEARCH_BACKEND_ELASTIC_SSL_ENABLED", 1)))
SEARCH_BACKEND_ELASTIC_SSL_VERIFY_CERTS = bool(int(os.environ.get("SEARCH_BACKEND_ELASTIC_SSL_VERIFY_CERTS", 1)))


class BackendNotDefinedError(Exception):
    """Raised when an unknown backend is configured."""


class SearchBackend:
    _client = None

    @property
    def client(self):
        if self._client is None:
            self.create_client()
        return self._client

    def create_client(self):
        raise NotImplementedError("create_client() must be defined")

    def query(self, search_term):
        raise NotImplementedError("query() must be defined")


class ElasticsearchBackend(SearchBackend):
    def __init__(self, host: str, api_key: str, index: str):
        super(ElasticsearchBackend, self).__init__()
        self.host = host
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

    def query(self, search_term):
        body = {
            "query": {
                "multi_match": {
                    "query": search_term,
                    # TODO: Check if there's any fields we might want to search on
                    "fields": ["title", "content"]
                }
            }
        }
        return self.client.search(index=self.index, body=body, filter_path=['hits.hits.title', 'hits.hits.path'])


def init_search_backend():
    backend = SEARCH_BACKEND.lower() if SEARCH_BACKEND else None
    if backend == "elasticsearch":
        from elasticsearch import Elasticsearch
        kwargs = {
            "api_key": os.environ['SEARCH_BACKEND_ELASTIC_API_TOKEN'],
            "host": os.environ['SEARCH_BACKEND_ELASTIC_HOST'],
            "index": os.environ['SEARCH_BACKEND_ELASTIC_INDEX']
        }
        return ElasticsearchBackend(**kwargs)
    else:
        raise BackendNotDefinedError(f"Backend '{backend}' is not defined.")
