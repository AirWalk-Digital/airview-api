from airview_api.models import MonitoredResourceState
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
        quality_model=models.QualityModel.SECURITY,
        type=models.TechnicalControlType.LOG,
        can_delete_resources=False,
        is_blocking=True,
        ttl=20,
    )
    evt = models.ComplianceEvent(
        application=application,
        technical_control=technical_control,
        resource_reference="res-ref-1",
        status=models.MonitoredResourceState.FLAGGED,
        type=models.MonitoredResourceType.VIRTUAL_MACHINE,
        additional_data="Additional",
    )

    yield evt


def setup():
    setup_factories()


def test_monitored_resource_creates_missing_system(handler, compliance_event):
    """
    Given: A missing system
    When: When a call is made to set a monitored resource
    Then: The monitored resource is persisted against a new system
    """
    print(compliance_event)
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )

    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].state == MonitoredResourceState.FLAGGED
    assert monitored[0].type == MonitoredResourceType.VIRTUAL_MACHINE
    assert monitored[0].reference == "res-ref-1"
    assert (
        monitored[0].application_technical_control.technical_control.system.name
        == "one"
    )
    assert (
        monitored[0].application_technical_control.technical_control.system.stage.name
        == "BUILD"
    )


def test_monitored_resource_persisted_for_linked(handler, compliance_event):
    """
    Given: An existing linked application
    When: When a call is made to set a monitored resource
    Then: The monitored resource is persisted
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )
    SystemFactory(id=111, name="one", stage=api_models.SystemStage.BUILD)
    TechnicalControlFactory(id=4, system_id=111, reference="tc-ref-1", severity="HIGH")
    ApplicationTechnicalControlFactory(id=5, application_id=2, technical_control_id=4)

    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].state == MonitoredResourceState.FLAGGED
    assert monitored[0].type == MonitoredResourceType.VIRTUAL_MACHINE
    assert monitored[0].reference == "res-ref-1"
    assert monitored[0].application_technical_control_id == 5


def test_triggered_resource_creates_new_control(handler, compliance_event):
    """
    Given: An existing linked application, no known control
    When: When a call is made to set a triggered resource
    Then: New control created and linked, the triggerend resource is sent to the backend
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )
    SystemFactory(id=111, name="one", stage=api_models.SystemStage.BUILD)
    TechnicalControlFactory(
        id=4, system_id=111, reference="tc-ref-other", severity="HIGH"
    )
    ApplicationTechnicalControlFactory(id=5, application_id=2, technical_control_id=4)

    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    tc = TechnicalControl.query.all()
    len(tc) == 2
    assert tc[1].name == "ctrl a"
    assert tc[1].reference == "tc-ref-1"
    assert tc[1].is_blocking == True
    assert tc[1].can_delete_resources == False
    assert tc[1].ttl == 20

    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].state == MonitoredResourceState.FLAGGED
    assert monitored[0].type == MonitoredResourceType.VIRTUAL_MACHINE
    assert monitored[0].reference == "res-ref-1"
    assert monitored[0].application_technical_control_id == 6


def test_triggered_resource_creates_new_control_with_parent(handler, compliance_event):
    """
    Given: An existing linked application, no known control, control has a parent
    When: When a call is made to set a triggered resource
    Then: New control created and linked to parent, the triggerend resource is sent to the backend
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )
    SystemFactory(id=111, name="one", stage=api_models.SystemStage.BUILD)
    TechnicalControlFactory(
        id=4, system_id=111, reference="tc-ref-other", severity="HIGH"
    )
    ApplicationTechnicalControlFactory(id=5, application_id=2, technical_control_id=4)

    # Act
    compliance_event.technical_control.parent_id = 4
    handler.handle_compliance_event(compliance_event)
    compliance_event.technical_control.parent_id = None

    # Assert
    tc = TechnicalControl.query.all()
    len(tc) == 2
    assert tc[1].name == "ctrl a"
    assert tc[1].reference == "tc-ref-1"
    assert tc[1].is_blocking == True
    assert tc[1].can_delete_resources == False
    assert tc[1].ttl == 20
    assert tc[1].parent_id == 4

    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].state == MonitoredResourceState.FLAGGED
    assert monitored[0].type == MonitoredResourceType.VIRTUAL_MACHINE
    assert monitored[0].reference == "res-ref-1"
    assert monitored[0].application_technical_control_id == 6


def test_triggered_resource_creates_new_control_with_defaults(
    handler, compliance_event
):
    """
    Given: An existing linked application, no known control
    When: When a call is made to set a triggered resource with missing optional fields
    Then: New control created with defaults and linked, the triggerend resource is sent to the backend
    """
    # Arrange
    EnvironmentFactory(id=1, name="Env One", abbreviation="ONE")
    ApplicationFactory(id=2, environment_id=1)
    ApplicationReferenceFactory(
        application_id=2, type="aws_account_id", reference="app-ref-1"
    )
    SystemFactory(id=111, name="one", stage=api_models.SystemStage.BUILD)
    TechnicalControlFactory(
        id=4, system_id=111, reference="tc-ref-other", severity="HIGH"
    )
    ApplicationTechnicalControlFactory(id=5, application_id=2, technical_control_id=4)

    # Act
    compliance_event.technical_control.ttl = None
    compliance_event.technical_control.can_delete_resources = None
    compliance_event.technical_control.is_blocking = None
    handler.handle_compliance_event(compliance_event)

    # Assert
    tc = TechnicalControl.query.all()
    len(tc) == 2
    assert tc[1].name == "ctrl a"
    assert tc[1].reference == "tc-ref-1"
    assert tc[1].is_blocking == False
    assert tc[1].can_delete_resources == True
    assert tc[1].ttl == None

    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1
    assert monitored[0].state == MonitoredResourceState.FLAGGED
    assert monitored[0].type == MonitoredResourceType.VIRTUAL_MACHINE
    assert monitored[0].reference == "res-ref-1"
    assert monitored[0].application_technical_control_id == 6


def test_triggered_resource_creates_new_app(handler, compliance_event):
    """
    Given: No existing linked application
    When: When a call is made to set a triggered resource
    Then: A new application is created, linked and triggered
    """
    # Arrange
    SystemFactory(id=111, name="one", stage=api_models.SystemStage.BUILD)

    # Act
    handler.handle_compliance_event(compliance_event)

    # Assert
    monitored = MonitoredResource.query.all()
    assert len(monitored) == 1

    app = Application.query.first()
    assert app.name == "app one"
    assert app.application_type == api_models.ApplicationType.BUSINESS_APPLICATION
    assert app.environment_id == None

    refs = app.references.all()
    assert len(refs) == 2
    assert refs[1].type == "aws_account_id"
    assert refs[1].reference == "app-ref-1"


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


def test_triggered_resource_handle_unexpected_code_for_get_app_technical_control(
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
        f"{base_url}/application-technical-controls/?applicationId=111&technicalControlId=222",
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


def test_triggered_resource_handle_unexpected_code_for_link_technical_control(
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
        f"{base_url}/application-technical-controls/?applicationId=111&technicalControlId=222",
        status_code=404,
    )

    adapter.register_uri(
        "POST",
        f"{base_url}/application-technical-controls/",
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
        f"{base_url}/application-technical-controls/?applicationId=111&technicalControlId=222",
        status_code=200,
        json={"id": 444},
    )

    adapter.register_uri(
        "PUT",
        f"{base_url}/monitored-resources/?applicationTechnicalControlId=444&reference=res-ref-1",
        status_code=500,
    )

    # Act
    with pytest.raises(models.BackendFailureException) as excinfo:
        handler.handle_compliance_event(compliance_event)
