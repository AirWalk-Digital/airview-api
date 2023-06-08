from tests.client_tests.common import *
from airview_api import app
from airview_api.database import db
from airview_api import models as api_models
from tests.common import client, instance
from tests.factories import *
import requests_mock
from requests_flask_adapter import Session
import pytest

from client.airviewclient import models


@pytest.fixture()
def mapped_resource():
    application = models.Application(name="app one", reference="app-ref-1")
    service = models.Service(name="svc_one", reference="svc-ref-1", type=models.ServiceType.CONTAINER)
    resource = models.Resource(name='res_one', reference='res-ref-1', application=application, service=service)

    yield resource


def setup():
    setup_factories()


def test_monitored_resource_creates_missing_application(handler, mapped_resource):
    """
    Given: A resource with a non-existing application
    When: When a call is made to create the resource
    Then: The monitored resource is persisted against a new application
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-other"
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    applications = Application.query.all()
    assert len(applications) == 2

    assert applications[1].name == mapped_resource.application.name 
    assert applications[1].references[1].reference == 'app-ref-1' 



def test_monitored_resource_creates_missing_service(handler, mapped_resource):
    """
    Given: A resource with a non-existing service
    When: When a call is made to create the resource
    Then: The monitored resource is persisted against a new service
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-other"
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    services = Service.query.all()
    assert len(services) == 2

    assert services[1].name == mapped_resource.service.name 
    assert services[1].reference == mapped_resource.service.reference 
    assert services[1].type.name == mapped_resource.service.type.name 





