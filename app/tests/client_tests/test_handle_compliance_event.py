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
def compliance_event():
    application = models.Application(name="app one", reference="app-ref-1")
    technical_control = models.TechnicalControl(
        name="ctrl a",
        reference="tc-ref-1",
        is_blocking=True,
        ttl=20,
        control_action=models.TechnicalControlAction.LOG,
    )
    evt = models.ComplianceEvent(
        application=application,
        technical_control=technical_control,
        resource_reference="res-ref-1",
        status=models.MonitoredResourceState.FLAGGED,
        additional_data="Additional",
    )

    yield evt


def setup():
    setup_factories()


def test_monitored_resource_creates_missing_application(handler, compliance_event):
    """
    Given: A compliance event with a non-existing application, existing technica control
    When: When a call is made to set a monitored resource
    Then: The monitored resource is persisted against a new application, new resource
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-other"
    )
    ResourceFactory(
        id=11,
        name="Res Other",
        reference="res-ref-other",
        service_id=10,
        application_id=2,
    )

    SystemFactory(id=111, stage=api_models.SystemStage.BUILD, name="one")

    TechnicalControlFactory(
        id=999,
        reference="tc-ref-1",
        name="one",
        system_id=111,
        control_action=TechnicalControlAction.LOG,
    )
    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].monitoring_state.name == "FLAGGED"
    assert monitored[0].resource_id == 12
    assert monitored[0].technical_control_id == 999

    assert monitored[0].resource.reference == "res-ref-1"
    assert monitored[0].resource.name == "res-ref-1"
    assert monitored[0].resource.application_id == 3


def test_monitored_resource_creates_missing_resource_existing_app(
    handler, compliance_event
):
    """
    Given: A compliance event with a existing application, existing technical control
    When: When a call is made to set a monitored resource
    Then: The monitored resource is persisted against a new application, new resource
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )
    ResourceFactory(
        id=11,
        name="Res Other",
        reference="res-ref-other",
        service_id=10,
        application_id=2,
    )

    SystemFactory(id=111, stage=api_models.SystemStage.BUILD, name="one")

    TechnicalControlFactory(
        id=999,
        reference="tc-ref-1",
        name="one",
        system_id=111,
        control_action=TechnicalControlAction.LOG,
    )
    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].monitoring_state.name == "FLAGGED"
    assert monitored[0].resource_id == 12
    assert monitored[0].technical_control_id == 999

    assert monitored[0].resource.reference == "res-ref-1"
    assert monitored[0].resource.name == "res-ref-1"
    assert monitored[0].resource.application_id == 2


def test_monitored_resource_creates_missing_control(handler, compliance_event):
    """
    Given: A compliance event with a existing resource, missing technical control
    When: When a call is made to set a monitored resource
    Then: The monitored resource is persisted against a new technical control
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )
    ResourceFactory(
        id=11,
        name="Res Existing",
        reference="res-ref-1",
        service_id=10,
        application_id=2,
    )

    SystemFactory(id=111, stage=api_models.SystemStage.BUILD, name="one")

    TechnicalControlFactory(
        id=999,
        reference="tc-ref-other",
        name="one",
        system_id=111,
        control_action=TechnicalControlAction.LOG,
    )
    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].monitoring_state.name == "FLAGGED"
    assert monitored[0].resource_id == 11
    assert monitored[0].technical_control_id == 1000

    assert monitored[0].resource.reference == "res-ref-1"
    assert monitored[0].resource.name == "Res Existing"
    assert monitored[0].resource.application_id == 2


def test_account_cache_handle_unexpected_code_for_get_control(
    handler, compliance_event, adapter
):
    """
    Given: Status code 500 returned by GET technical control
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri(
        "GET",
        f"{base_url}/systems/?name=one",
        status_code=200,
        json={
            "id": 111,
            "name": "name",
        },
    )

    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=app-ref-1",
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
    adapter.register_uri(
        "GET",
        f"{base_url}/technical-controls/?systemId=111&reference=tc-ref-1",
        status_code=500,
    )
    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_compliance_event(compliance_event)


def test_triggered_resource_handle_unexpected_code_for_get_resource(
    handler, adapter, compliance_event
):
    """
    Given: Status code 500 returned by GET application technical control
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    # Arrange
    adapter.register_uri(
        "GET",
        f"{base_url}/systems/?name=one",
        status_code=200,
        json={
            "id": 111,
            "name": "name",
        },
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=app-ref-1",
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
    adapter.register_uri(
        "GET",
        f"{base_url}/technical-controls/?systemId=111&reference=tc-ref-1",
        status_code=200,
        json=[
            {
                "id": 222,
                "name": "tc1",
                "reference": "ref1",
                "qualityModel": "SECURITY",
                "controlAction": "LOG",
            }
        ],
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/resources/?applicationId=111&reference=res-ref-1",
        status_code=500,
    )
    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_compliance_event(compliance_event)


def test_triggered_resource_handle_unexpected_code_for_create_technical_control(
    handler, adapter, compliance_event
):
    """
    Given: Status code 500 returned by POST technical-control
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    adapter.register_uri(
        "GET",
        f"{base_url}/systems/?name=one",
        status_code=200,
        json={
            "id": 111,
            "name": "name",
        },
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=app-ref-1",
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
    adapter.register_uri(
        "GET",
        f"{base_url}/technical-controls/?systemId=111&reference=tc-ref-1",
        status_code=200,
        json=[],
    )
    adapter.register_uri(
        "POST",
        f"{base_url}/technical-controls/",
        status_code=500,
    )
    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_compliance_event(compliance_event)


def test_triggered_resource_handle_unexpected_code_for_create_resource(
    handler, adapter, compliance_event
):
    """
    Given: Status code 500 returned by POST application-technical-control
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    adapter.register_uri(
        "GET",
        f"{base_url}/systems/?name=one",
        status_code=200,
        json={
            "id": 111,
            "name": "name",
        },
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=app-ref-1",
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
    adapter.register_uri(
        "GET",
        f"{base_url}/technical-controls/?systemId=111&reference=tc-ref-1",
        status_code=200,
        json=[
            {
                "id": 222,
                "name": "tc1",
                "reference": "ref1",
                "qualityModel": "SECURITY",
                "controlAction": "LOG",
            }
        ],
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/resources/?applicationId=111&reference=res-ref-1",
        status_code=404,
    )

    adapter.register_uri(
        "POST",
        f"{base_url}/resources/",
        status_code=500,
    )

    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_compliance_event(compliance_event)


def test_triggered_resource_handle_unexpected_code_for_monitored_resource(
    handler, adapter, compliance_event
):
    """
    Given: Status code 500 returned by PUT monitored resource
    When: When a call is made to set a triggered resource
    Then: An exception is raised
    """
    adapter.register_uri(
        "GET",
        f"{base_url}/systems/?name=one",
        status_code=200,
        json={
            "id": 111,
            "name": "name",
        },
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/referenced-applications/?type=aws_account_id&reference=app-ref-1",
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
    adapter.register_uri(
        "GET",
        f"{base_url}/technical-controls/?systemId=111&reference=tc-ref-1",
        status_code=200,
        json=[
            {
                "id": 222,
                "name": "tc1",
                "reference": "ref1",
                "qualityModel": "SECURITY",
                "controlAction": "LOG",
            }
        ],
    )
    adapter.register_uri(
        "GET",
        f"{base_url}/resources/?applicationId=111&reference=res-ref-1",
        status_code=200,
        json={"id": 444},
    )

    adapter.register_uri(
        "PUT",
        f"{base_url}/monitored-resources/?technicalControlId=222&resourceId=444",
        status_code=500,
    )

    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_compliance_event(compliance_event)
