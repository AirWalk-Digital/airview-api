import os

import pytest
import airview_api.search

from airview_api.schemas import SearchResultSchema
from airview_api.search import SearchBackendNotDefinedError, init_search_backend, ElasticsearchBackend
from unittest.mock import patch
from tests.common import client


@pytest.fixture
def mock_search_response():
    return {
        'hits': {
            'hits': [{
                '_source': {
                    'path': '/applications/microsoft_teams/knowledge/backgrounds/_index.md',
                    'title': 'MS Teams – Meeting backgrounds'
                },
                'highlight': {
                    'content': [
                        'Change your background before a meeting starts   While',
                        'setting up your video and audio before joining a meeting',
                        'Change your background during a meeting   Go to your',
                        'meeting controls and select More actions > Apply background'
                    ]
                }
            }]
        }
    }


def test_search_backend_is_undefined():
    airview_api.search.SEARCH_BACKEND = None
    backend = init_search_backend()
    assert backend is None


def test_search_endpoint_raises_unknown_backend():
    airview_api.search.SEARCH_BACKEND = "rigidsearch"
    with pytest.raises(SearchBackendNotDefinedError):
        init_search_backend()


def test_search_endpoint_without_backend(client):
    # Ensure no SEARCH_BACKEND in environment
    airview_api.search.SEARCH_BACKEND = None
    resp = client.get("/search/?q=something")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []


def test_search_endpoint_without_query(client):
    airview_api.search.SEARCH_BACKEND = None
    resp = client.get("/search/")
    assert resp.status_code == 422


def test_elasticsearch_backend_is_initialised():
    airview_api.search.SEARCH_BACKEND = "elasticsearch"
    mock_env_vars = {
        "SEARCH_BACKEND_ELASTIC_API_TOKEN": "a",
        "SEARCH_BACKEND_ELASTIC_HOST": "local",
        "SEARCH_BACKEND_ELASTIC_INDEX": "test"
    }
    with patch. dict(os.environ, mock_env_vars, clear=True):
        backend = init_search_backend()
        assert isinstance(backend, ElasticsearchBackend)


@patch("elasticsearch.Elasticsearch.search")
def test_elasticsearch_backend(mock_search, mock_search_response):
    mock_search.return_value = mock_search_response
    backend = ElasticsearchBackend(
        host="test",
        api_key="high_entropy_string",  # pragma: allowlist secret
        index="random"
    )
    result = backend.query(q="teams")
    assert result == [
        {
            'path': '/applications/microsoft_teams/knowledge/backgrounds/_index.md',
            'title': 'MS Teams – Meeting backgrounds',
            'summary': "Change your background before a meeting starts   While\n"
                       "setting up your video and audio before joining a meeting\n"
                       "Change your background during a meeting   Go to your\n"
                       "meeting controls and select More actions > Apply background"
        }
    ]
    valid_schema = SearchResultSchema(many=True).validate(result)
    assert valid_schema == {}
