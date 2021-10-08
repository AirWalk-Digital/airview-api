from tests.common import client
from tests.factories import *
import requests_mock
from requests_flask_adapter import Session
import pytest
from client.airviewclient.client import _get_handler
from client.airviewclient.models import BackendConfig

base_url = "mock://someres"


@pytest.fixture
def session(instance):
    # Allows endpoints to have their http responses mocked (i.e. not calling the backend api code)
    Session.register("mock://someres", instance)
    session = Session()
    return session


@pytest.fixture
def adapter(session):
    # Allows us to call backend api code outside of a flask server to prevent regressions if api changes and this client code does not
    adapter = requests_mock.Adapter()
    session.mount(base_url, adapter)
    return adapter


@pytest.fixture
def handler(session):
    backend_config = BackendConfig(
        base_url=base_url,
        token="dummy_token",
        system_id=111,
        referencing_type="aws_account_id",
    )
    handler = _get_handler(session=session, backend_config=backend_config)
    return handler


def setup_factories():
    reset_factories()
    ApplicationTypeFactory(id=1)
