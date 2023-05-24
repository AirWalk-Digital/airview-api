from datetime import datetime, timezone
from pprint import pprint
from tests.factories import *
from tests.common import client
from airview_api.models import (
    Application,
    ApplicationTechnicalControl,
    MonitoredResource,
    TechnicalControlSeverity,
    TechnicalControlAction,
    MonitoredResourceState,
    SystemStage,
)


def setup():
    reset_factories()


def test_create_rejects_bad_reference(client):
    """
    Given: No existing data
    When: When the api is called to create a new monitored resource with url escape chars in reference
    Then: 422 status, no data persisted
    """
    # Arrange
    input_data = {"type": "VIRTUAL_MACHINE", "monitoringState": "FLAGGED"}
    # Act

    resp = client.put(
        "/monitored-resources/?applicationTechnicalControlid=2,stage=SystemStage.BUILD01&reference=ref$1",
        json=input_data,
    )
    assert resp.status_code == 422

    items = MonitoredResource.query.all()
    assert len(items) == 0


def test_create_adds_when_new(client):
    """
    Given: existing linked apps and controls
    When: When the api is called to create a new monitored resource
    Then: 204 status, no data returned, data persisted
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(id=1)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_action=TechnicalControlAction.LOG,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=201, application_id=1, technical_control_id=101
    )

    input_data = {
        "monitoringState": "FLAGGED",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?applicationTechnicalControlId=201&resourceId=99",
        json=input_data,
    )
    assert resp.status_code == 204

    items = MonitoredResource.query.all()
    assert len(items) == 1

    persisted = MonitoredResource.query.first()
    assert persisted.application_technical_control_id == 201
    assert persisted.reference == "ref-1"
    assert persisted.type == MonitoredResourceType.VIRTUAL_MACHINE
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
    ApplicationFactory(id=1)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_action=TechnicalControlAction.LOG,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=201, application_id=1, technical_control_id=101
    )
    item = MonitoredResourceFactory(
        id=301,
        reference="ref-1",
        monitoring_state=MonitoredResourceState.FLAGGED,
        application_technical_control_id=201,
        last_modified=datetime(2001, 1, 1, tzinfo=timezone.utc),
        last_seen=datetime(2002, 1, 1, tzinfo=timezone.utc),
        additional_data="Old",
    )

    input_data = {
        "type": "VIRTUAL_MACHINE",
        "monitoringState": "SUPPRESSED",
        "additionalData": "Additional",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?applicationTechnicalControlId=201&reference=ref-1",
        json=input_data,
    )
    assert resp.status_code == 204

    items = MonitoredResource.query.all()
    assert len(items) == 1

    persisted = MonitoredResource.query.first()
    assert persisted.application_technical_control_id == 201
    assert persisted.reference == "ref-1"
    assert persisted.type == MonitoredResourceType.VIRTUAL_MACHINE
    assert persisted.state == MonitoredResourceState.SUPPRESSED
    assert persisted.last_modified > datetime(2001, 1, 1, tzinfo=timezone.utc)
    assert persisted.last_seen > datetime(2002, 1, 1, tzinfo=timezone.utc)
    assert persisted.additional_data == "Additional"


def test_create_updates_when_existing_same_state(client):
    """
    Given: existing monitored resource
    When: When the api is called to create a persist monitored resource with same state
    Then: 204 status, no data returned, last_updated updates, last_modified not
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(id=1)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_action=TechnicalControlAction.LOG,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=201, application_id=1, technical_control_id=101
    )
    MonitoredResourceFactory(
        id=301,
        reference="ref-1",
        monitoring_state=MonitoredResourceState.FLAGGED,
        application_technical_control_id=201,
        last_modified=datetime(2001, 1, 1, tzinfo=timezone.utc),
        last_seen=datetime(2002, 1, 1, tzinfo=timezone.utc),
        additional_data="Old",
    )

    input_data = {
        "type": "VIRTUAL_MACHINE",
        "monitoringState": "FLAGGED",
        "additionalData": "Additional",
    }
    # Act

    resp = client.put(
        "/monitored-resources/?applicationTechnicalControlId=201&reference=ref-1",
        json=input_data,
    )
    assert resp.status_code == 204

    items = MonitoredResource.query.all()
    assert len(items) == 1

    persisted = MonitoredResource.query.first()
    assert persisted.application_technical_control_id == 201
    assert persisted.reference == "ref-1"
    assert persisted.type == MonitoredResourceType.VIRTUAL_MACHINE
    assert persisted.state == MonitoredResourceState.FLAGGED
    assert persisted.last_modified == datetime(2001, 1, 1, tzinfo=timezone.utc)
    assert persisted.last_seen > datetime(2002, 1, 1, tzinfo=timezone.utc)
    assert persisted.additional_data == "Additional"
