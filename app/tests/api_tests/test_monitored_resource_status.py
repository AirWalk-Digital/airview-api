from datetime import datetime, timedelta, timezone
from pprint import pprint
from tests.factories import *
from tests.common import client
from airview_api.models import (
    MonitoredResource,
    MonitoredResourceState,
    SystemStage,
    TechnicalControlAction,
)


def setup():
    reset_factories()


def test_create_adds_when_new(client):
    """
    Given: existing linked apps and controls
    When: When the api is called to create a new monitored resource
    Then: 204 status, no data returned, data persisted
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(
        id=1, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )
    EnvironmentFactory(id=3)
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=3)

    ResourceTypeFactory(
        id=10, name="res type one", reference="res-type-1", service_id=10
    )
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    TechnicalControlFactory(
        id=1,
        reference="1",
        name="one",
        system_id=2,
        control_action=TechnicalControlAction.LOG,
    )
    ResourceFactory(
        id=11,
        name="Res One",
        reference="res_1",
        resource_type_id=10,
        application_environment_id=1,
    )

    input_data = {
        "monitoringState": "FLAGGED",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?technicalControlId=1&resourceId=11",
        json=input_data,
    )
    assert resp.status_code == 204

    items = MonitoredResource.query.all()
    assert len(items) == 1

    persisted = MonitoredResource.query.first()
    assert persisted.resource_id == 11
    assert persisted.technical_control_id == 1
    assert persisted.monitoring_state == MonitoredResourceState.FLAGGED
    assert persisted.additional_data == ""


def test_create_updates_when_existing_different_state(client):
    """
    Given: existing monitored resource
    When: When the api is called to create a persist monitored resource with same state
    Then: 204 status, no data returned, last_updated updates, last_modified not
    """
    # Arrange

    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(
        id=1, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )

    EnvironmentFactory(id=3)
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=3)

    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ResourceTypeFactory(
        id=10, name="res type one", reference="res-type-1", service_id=10
    )

    TechnicalControlFactory(
        id=1,
        reference="1",
        name="one",
        system_id=2,
    )
    ResourceFactory(
        id=11,
        name="Res One",
        reference="res_1",
        resource_type_id=10,
        application_environment_id=1,
    )

    time_now = datetime.utcnow()

    item = MonitoredResourceFactory(
        id=301,
        resource_id=11,
        technical_control_id=1,
        monitoring_state=MonitoredResourceState.FLAGGED,
        last_modified=time_now,
        last_seen=time_now - timedelta(days=1),
        additional_data="Old",
    )

    input_data = {
        "monitoringState": "FLAGGED",
        "additionalData": "Old",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?technicalControlId=1&resourceId=11",
        json=input_data,
    )
    assert resp.status_code == 204

    items = MonitoredResource.query.all()
    assert len(items) == 1

    persisted = MonitoredResource.query.first()
    assert persisted.resource_id == 11
    assert persisted.technical_control_id == 1
    assert persisted.monitoring_state == MonitoredResourceState.FLAGGED
    assert persisted.last_modified == time_now
    assert persisted.last_seen > time_now
    assert persisted.additional_data == "Old"


def test_create_unknown_technical_control(client):
    """
    Given: unknown technical control, known resource
    When: When the api is called to create a new monitored resource
    Then: 400 status, no data returned, no data persisted
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(
        id=1, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )

    EnvironmentFactory(id=3)
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=3)
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    TechnicalControlFactory(
        id=1,
        reference="1",
        name="one",
        system_id=2,
    )
    ResourceFactory(
        id=11,
        name="Res One",
        reference="res_1",
        resource_type_id=10,
        application_environment_id=1,
    )

    input_data = {
        "monitoringState": "FLAGGED",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?technicalControlId=9999&resourceId=11",
        json=input_data,
    )
    assert resp.status_code == 400

    items = MonitoredResource.query.all()
    assert len(items) == 0


def test_create_unknown_resource(client):
    """
    Given: no existing technical control, existing app
    When: When the api is called to create a new monitored resource
    Then: 400 status, no data returned, no data persisted
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(
        id=1, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )
    EnvironmentFactory(id=3)
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=3)

    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    TechnicalControlFactory(
        id=1,
        reference="1",
        name="one",
        system_id=2,
    )
    ResourceFactory(
        id=11,
        name="Res One",
        reference="res_1",
        resource_type_id=10,
        application_environment_id=1,
    )

    input_data = {
        "monitoringState": "FLAGGED",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?technicalControlId=1&resourceId=9999",
        json=input_data,
    )
    assert resp.status_code == 400

    items = MonitoredResource.query.all()
    assert len(items) == 0
