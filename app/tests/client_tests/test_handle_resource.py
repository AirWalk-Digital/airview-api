from tests.client_tests.common import *
from airview_api import app
from airview_api.database import db
from airview_api import models as api_models
from tests.common import client, instance
from tests.factories import *
import requests_mock
from requests_flask_adapter import Session
import pytest
from pprint import pprint

from client.airviewclient import models


@pytest.fixture()
def mapped_resource():
    application = models.Application(name="app one", reference="app-ref-1")
    service = models.Service(
        name="svc_one", reference="svc-ref-1", type=models.ServiceType.CONTAINER
    )
    resource_type = models.ResourceType(
        name="res type one", reference="res-type-1", service=service
    )
    resource = models.Resource(
        name="res_one",
        reference="res-ref-1",
        application=application,
        resource_type=resource_type,
    )

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
    ServiceFactory(id=10, name="Service One", reference="svc-ref-1", type="NETWORK")
    ResourceTypeFactory(
        id=10, name="res type one", reference="res-type-1", service_id=10
    )

    ApplicationFactory(id=2)
    ApplicationEnvironmentFactory(id=1, application_id=2, environment_id=1)
    ApplicationEnvironmentReferenceFactory(
        application_environment_id=1, type="aws_account_id", reference="app-ref-other"
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    application_environments = api_models.ApplicationEnvironment.query.all()
    assert len(application_environments) == 2

    assert (
        application_environments[1].application.name == mapped_resource.application.name
    )

    assert application_environments[1].references[0].reference == "app-ref-1"

    # Assert new resource
    resources = api_models.Resource.query.all()
    assert len(resources) == 1
    assert resources[0].name == mapped_resource.name
    assert resources[0].reference == mapped_resource.reference
    assert resources[0].application_environment_id == 2
    assert resources[0].resource_type_id == 10
    assert resources[0].resource_type.reference == "res-type-1"
    assert resources[0].resource_type.name == "res type one"


def test_monitored_resource_creates_missing_resource_type(handler, mapped_resource):
    """
    Given: A resource with a non-existing resource type, exisiting service
    When: When a call is made to create the resource
    Then: The monitored resource is persisted against a new resource type
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2)
    ApplicationEnvironmentFactory(id=1, application_id=2, environment_id=1)
    ApplicationEnvironmentReferenceFactory(
        application_environment_id=1, type="aws_account_id", reference="app-ref-1"
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    resource_types = api_models.ResourceType.query.all()
    assert len(resource_types) == 1

    assert resource_types[0].name == mapped_resource.resource_type.name
    assert resource_types[0].reference == mapped_resource.resource_type.reference

    pprint(resource_types[0].service.reference)
    assert (
        resource_types[0].service.reference
        == mapped_resource.resource_type.service.reference
    )

    # Assert new resource
    resources = api_models.Resource.query.all()
    assert len(resources) == 1
    assert resources[0].name == mapped_resource.name
    assert resources[0].reference == mapped_resource.reference
    assert resources[0].application_environment_id == 1
    assert resources[0].resource_type_id == 1
    assert resources[0].resource_type.reference == "res-type-1"
    assert resources[0].resource_type.name == "res type one"


def test_monitored_resource_creates_missing_service(handler, mapped_resource):
    """
    Given: A resource with a non-existing service and resource type
    When: When a call is made to create the resource
    Then: The monitored resource is persisted against a new service & resource type
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2)
    ApplicationEnvironmentFactory(id=1, application_id=2, environment_id=1)
    ApplicationEnvironmentReferenceFactory(
        application_environment_id=1, type="aws_account_id", reference="app-ref-1"
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    services = api_models.Service.query.all()
    assert len(services) == 2

    assert services[1].name == mapped_resource.resource_type.service.name
    assert services[1].reference == mapped_resource.resource_type.service.reference
    assert services[1].type.name == mapped_resource.resource_type.service.type

    # Assert new resource
    resources = api_models.Resource.query.all()
    assert len(resources) == 1
    assert resources[0].name == mapped_resource.name
    assert resources[0].reference == mapped_resource.reference
    assert resources[0].application_environment_id == 1
    assert resources[0].resource_type.service_id == 11
    assert resources[0].resource_type.reference == "res-type-1"
    assert resources[0].resource_type.name == "res type one"


def test_monitored_resource_use_pre_existing_dependents(handler, mapped_resource):
    """
    Given: A resource with existing dependencies
    When: When a call is made to create the resource
    Then: The monitored resource is persisted against the pre-existing dependencies
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="svc-ref-1", type="NETWORK")
    ResourceTypeFactory(
        id=11, name="res type one", reference="res-type-1", service_id=10
    )

    ApplicationFactory(id=2)
    ApplicationEnvironmentFactory(id=1, application_id=2, environment_id=1)
    ApplicationEnvironmentReferenceFactory(
        application_environment_id=1, type="aws_account_id", reference="app-ref-1"
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    # Assert no new dependencies
    services = api_models.Service.query.all()
    assert len(services) == 1

    applications = api_models.Application.query.all()
    assert len(applications) == 1
    # Assert new resource
    resources = api_models.Resource.query.all()
    assert len(resources) == 1
    assert resources[0].name == mapped_resource.name
    assert resources[0].reference == mapped_resource.reference
    assert resources[0].application_environment_id == 1
    assert resources[0].resource_type.service_id == 10
    assert resources[0].resource_type.id == 11
    assert resources[0].resource_type.reference == "res-type-1"
    assert resources[0].resource_type.name == "res type one"


def test_monitored_resource_updates_existing(handler, mapped_resource):
    """
    Given: A resource with existing dependencies
    When: When a call is made to create the resource
    Then: The monitored resource is persisted against the pre-existing dependencies
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="svc-ref-1", type="NETWORK")
    ResourceTypeFactory(
        id=11, name="res type one", reference="res-type-1", service_id=10
    )

    ApplicationFactory(id=2)
    ApplicationEnvironmentFactory(id=1, application_id=2, environment_id=1)
    ApplicationEnvironmentReferenceFactory(
        application_environment_id=1, type="aws_account_id", reference="app-ref-1"
    )

    ResourceFactory(
        id=11,
        name="Res Other",
        reference="res-ref-1",
        resource_type_id=11,
        application_environment_id=1,
    )

    # Act
    handler.handle_resource(mapped_resource)

    # Assert
    # Assert dependencies
    services = api_models.Service.query.all()
    assert len(services) == 1

    applications = api_models.Application.query.all()
    assert len(applications) == 1
    # Assert new resource
    resources = api_models.Resource.query.all()
    assert len(resources) == 1

    assert resources[0].name == mapped_resource.name
    assert resources[0].reference == mapped_resource.reference
    assert resources[0].application_environment_id == 1
    assert resources[0].resource_type_id == 11
