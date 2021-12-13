from tests.client_tests.common import *
from airview_api import app
from airview_api.database import db
from tests.common import client, instance
from tests.factories import *
import requests_mock
from requests_flask_adapter import Session
import pytest
from airview_api import models as api_models

from client.airviewclient import models


def setup():
    global application
    application = models.Application(
        name="Test App",
        reference="ref-1",
        environment=models.Environment(name="Env One", abbreviation="ONE"),
    )

    setup_factories()


def test_account_cache_does_not_recreate_environment_when_exists(handler):
    """
    Given: An existing environment
    When: When a call is made to persist an account
    Then: The existing environment is reused
    """
    # Arrange
    EnvironmentFactory(name="Env original name", abbreviation="ONE", id=99)

    # Act
    resp = handler.handle_application(application)

    # Assert
    envs = Environment.query.all()
    assert len(envs) == 1
    assert envs[0].name == "Env original name"
    assert envs[0].abbreviation == "ONE"

    assert resp.environment.name == "Env original name"
    assert resp.environment.abbreviation == "ONE"
    assert resp.environment.id == 99


def test_account_cache_creates_missing_environment(handler):
    """
    Given: An existing environment
    When: When a call is made to persist an account
    Then: The existing environment is reused
    """
    # Arrange
    envs = Environment.query.all()
    EnvironmentFactory(name="Other Env", abbreviation="XXX")
    envs = Environment.query.all()  #
    # Act
    handler.handle_application(application)

    # Assert
    envs = Environment.query.all()
    assert len(envs) == 2
    assert envs[1].name == "Env One"
    assert envs[1].abbreviation == "ONE"


def test_account_cache_creates_missing_application_existing_environment(handler):
    """
    Given: An existing environment, no app found
    When: When a call is made to persist an account
    Then: The existing environment is reused and new app created
    """
    # Arrange
    EnvironmentFactory(id=99, name="Env One", abbreviation="ONE")

    # Act
    resp = handler.handle_application(application)

    # Assert
    apps = Application.query.all()
    assert len(apps) == 1
    data = apps[0]
    assert data.name == "Test App"
    assert data.application_type == api_models.ApplicationType.BUSINESS_APPLICATION
    assert data.environment_id == 99

    refs = data.references.all()
    assert len(refs) == 2
    assert refs[1].type == "aws_account_id"
    assert refs[1].reference == "ref-1"

    # assert return
    assert resp.name == "Test App"
    assert resp.reference == "ref-1"
    assert resp.environment.name == "Env One"
    assert resp.environment.abbreviation == "ONE"
    assert resp.environment.id == 99
    assert resp.type == models.ApplicationType.BUSINESS_APPLICATION
    assert resp.id == 1
    assert resp.parent_id == None


def test_account_cache_creates_missing_application_with_parent(handler):
    """
    Given: A new app with valid parent
    When: When a call is made to persist an account
    Then: The parent is set on the child app
    """
    # Arrange
    EnvironmentFactory(id=99, name="Env One", abbreviation="ONE")
    ApplicationFactory(id=88, name="name123", environment_id=99)
    application.parent_id = 88

    # Act
    resp = handler.handle_application(application)

    # Assert
    apps = Application.query.all()
    assert len(apps) == 2
    data = apps[1]
    assert data.name == "Test App"
    assert data.application_type == api_models.ApplicationType.BUSINESS_APPLICATION
    assert data.environment_id == 99

    refs = data.references.all()
    assert len(refs) == 2
    assert refs[1].type == "aws_account_id"
    assert refs[1].reference == "ref-1"

    # assert return
    assert resp.name == "Test App"
    assert resp.reference == "ref-1"
    assert resp.environment.name == "Env One"
    assert resp.environment.abbreviation == "ONE"
    assert resp.environment.id == 99
    assert resp.type == models.ApplicationType.BUSINESS_APPLICATION
    assert resp.id == 89
    assert resp.parent_id == 88


def test_account_cache_creates_handle_bad_parent(handler):
    """
    Given: An existing environment, no app found
    When: When a call is made to persist an account with a invalid parent
    Then: BackendFailureException
    """
    # Arrange
    EnvironmentFactory(id=99, name="Env One", abbreviation="ONE")
    application.parent_id = 88

    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        resp = handler.handle_application(application)


def test_account_cache_creates_missing_application_missing_environment(handler):
    """
    Given: No existing environment, no app found
    When: When a call is made to persist an account
    Then: The new environment is used and new app created
    """
    # Arrange

    # Act
    resp = handler.handle_application(application)

    # Assert
    apps = Application.query.all()
    assert len(apps) == 1
    data = apps[0]
    assert data.name == "Test App"
    assert data.application_type == api_models.ApplicationType.BUSINESS_APPLICATION
    assert data.environment_id == 1

    refs = data.references.all()
    assert len(refs) == 2
    assert refs[1].type == "aws_account_id"
    assert refs[1].reference == "ref-1"

    # assert return
    assert resp.name == "Test App"
    assert resp.reference == "ref-1"
    assert resp.environment.name == "Env One"
    assert resp.environment.abbreviation == "ONE"
    assert resp.environment.id == 1
    assert resp.type == models.ApplicationType.BUSINESS_APPLICATION
    assert resp.id == 1
    assert resp.parent_id == None


def test_account_cache_updates_existing_application(handler):
    """
    Given: Existing application
    When: When a call is made to persist an application
    Then: The application is updated
    """
    # Arrange
    EnvironmentFactory(id=99, name="Other", abbreviation="XXX")
    ApplicationFactory(
        id=88,
        name="name123",
        application_type=api_models.ApplicationType.APPLICATION_SERVICE,
        environment_id=99,
    )
    ApplicationReferenceFactory(
        application_id=88, type="aws_account_id", reference="ref-1"
    )
    # Act
    resp = handler.handle_application(application)

    # Assert
    apps = Application.query.all()
    assert len(apps) == 1
    data = Application.query.get(88)
    assert data.name == "Test App"
    assert data.application_type == api_models.ApplicationType.BUSINESS_APPLICATION
    assert data.environment_id == 100

    refs = data.references.all()
    assert len(refs) == 1
    assert refs[0].type == "aws_account_id"
    assert refs[0].reference == "ref-1"

    # assert return
    assert resp.name == "Test App"
    assert resp.reference == "ref-1"
    assert resp.environment.name == "Env One"
    assert resp.environment.abbreviation == "ONE"
    assert resp.environment.id == 100
    assert resp.type == models.ApplicationType.BUSINESS_APPLICATION
    assert resp.id == 88
    assert resp.parent_id == None


def test_account_cache_updates_existing_application_handle_missing_parent(handler):
    """
    Given: Existing application
    When: When a call is made to persist an application with no parent
    Then: The application is saved without overwritng the parent
    """
    # Arrange
    # Arrange
    EnvironmentFactory(id=99, name="Other", abbreviation="XXX")
    ApplicationFactory(id=77)
    ApplicationFactory(id=88, name="name123", environment_id=99, parent_id=77)
    ApplicationReferenceFactory(
        application_id=88, type="aws_account_id", reference="ref-1"
    )
    # Act
    resp = handler.handle_application(application)

    # Assert
    apps = Application.query.all()
    assert len(apps) == 2
    data = Application.query.get(88)
    assert data.name == "Test App"
    assert data.application_type == api_models.ApplicationType.BUSINESS_APPLICATION
    assert data.environment_id == 100
    assert data.parent_id == 77

    refs = data.references.all()
    assert len(refs) == 1
    assert refs[0].type == "aws_account_id"
    assert refs[0].reference == "ref-1"

    # assert return
    assert resp.name == "Test App"
    assert resp.reference == "ref-1"
    assert resp.environment.name == "Env One"
    assert resp.environment.abbreviation == "ONE"
    assert resp.environment.id == 100
    assert resp.type == models.ApplicationType.BUSINESS_APPLICATION
    assert resp.id == 88
    assert resp.parent_id == 77


def test_account_cache_handle_unexpected_code_for_get_environment(handler, adapter):
    """
    Given: Status code 500 returned by GET environments
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri("GET", f"{base_url}/environments/", status_code=500)

    # Act
    with pytest.raises(Exception) as excinfo:
        handler.handle_application(application)


def test_account_cache_handle_unexpected_code_for_post_environment(handler, adapter):
    """
    Given: Status code 500 returned by GET environments
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri("GET", f"{base_url}/environments/", status_code=200, json=[])
    adapter.register_uri("POST", f"{base_url}/environments/", status_code=500)

    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_application(application)


def test_account_cache_handle_unexpected_code_for_get_app(handler, adapter):
    """
    Given: Status code 500 returned by GET app by system
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri(
        "GET",
        f"{base_url}/environments/",
        status_code=200,
        json=[{"id": 2, "name": "Env One", "abbreviation": "ONE"}],
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=ref-1",
        status_code=500,
    )

    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_application(application)


def test_account_cache_handle_unexpected_code_for_put_app(handler, adapter):
    """
    Given: Status code 500 returned by PUT application
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri(
        "GET",
        f"{base_url}/environments/",
        status_code=200,
        json=[{"id": 2, "name": "Env One", "abbreviation": "ONE"}],
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=ref-1",
        status_code=200,
        json={
            "id": 111,
            "name": "app-name",
            "reference": "app-ref",
            "applicationTypeId": 222,
            "environmentId": 333,
            "parentId": 444,
        },
    )
    adapter.register_uri("PUT", f"{base_url}/applications/111", status_code=500)
    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_application(application)


def test_account_cache_handle_unexpected_code_for_post_app(handler, adapter):
    """
    Given: Status code 500 returned by PUT application
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri(
        "GET",
        f"{base_url}/environments/",
        status_code=200,
        json=[{"id": 2, "name": "Env One", "abbreviation": "ONE"}],
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=ref-1",
        status_code=404,
    )
    adapter.register_uri("POST", f"{base_url}/applications/", status_code=500)
    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_application(application)
