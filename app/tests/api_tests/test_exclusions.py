from datetime import datetime
import pytest
from pprint import pprint
from airview_api.models import (
    TechnicalControlSeverity,
    Exclusion,
    ExclusionState,
    MonitoredResourceState,
    SystemStage,
    TechnicalControlAction,
)
from tests.common import client
from tests.factories import *
from dateutil import parser


def setup():
    reset_factories()

    SystemFactory(id=1, name="one", stage=SystemStage.BUILD)
    SystemFactory(id=2, name="two", stage=SystemStage.BUILD)
    EnvironmentFactory(id=1)
    ApplicationFactory(id=11, parent_id=None, name="svc 13", environment_id=1)
    ApplicationReferenceFactory(
        id=311, application_id=11, type="app-ref", reference="app-11"
    )
    TechnicalControlFactory(
        id=22,
        name="ctl1",
        reference="control_a",
        control_action=TechnicalControlAction.LOG,
        system_id=1,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=230,
        name="ctl2",
        reference="control_5",
        control_action=TechnicalControlAction.LOG,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=33, application_id=11, technical_control_id=22
    )
    ApplicationTechnicalControlFactory(
        id=340, application_id=11, technical_control_id=230
    )


def add_get_items_to_db():
    ExclusionFactory(
        id=44,
        application_technical_control_id=33,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1),
        notes="nnn",
    )
    MonitoredResourceFactory(
        id=55,
        exclusion_id=44,
        reference="res-a",
        exclusion_state=ExclusionState.PENDING,
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=33,
    )

    # unexpected other data
    ApplicationFactory(id=12, parent_id=None, name="svc 13", environment_id=1)
    ApplicationReferenceFactory(
        id=312, application_id=12, type="app-ref", reference="app-svc-13"
    )
    ApplicationTechnicalControlFactory(
        id=34, application_id=12, technical_control_id=22
    )

    ExclusionFactory(
        id=45,
        application_technical_control_id=340,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1),
        notes="nnn",
    )
    MonitoredResourceFactory(
        id=56,
        exclusion_id=45,
        reference="res-5",
        exclusion_state=ExclusionState.PENDING,
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=340,
    )
    MonitoredResourceFactory(
        id=57,
        exclusion_id=45,
        reference="res-6",
        exclusion_state=ExclusionState.ACTIVE,
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=340,
    )


def test_exclusions_post_ok_for_new_resources(client):
    """
    Given: An empty exclusions colllection, linked app controls, existing resources
    When: When the api is called with an exclusion request
    Then: The exclusions request is persisted & linked to existing resources, 201 status
    """
    # Arrange
    MonitoredResourceFactory(
        application_technical_control_id=33,
        reference="res-a",
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
    )
    MonitoredResourceFactory(
        application_technical_control_id=33,
        reference="res-b",
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
    )

    data = {
        "applicationTechnicalControlId": 33,
        "summary": "sum a",
        "mitigation": "mit b",
        "probability": 1,
        "impact": 2,
        "resources": ["res-c", "res-d"],
        "isLimitedExclusion": True,
        "endDate": "2022-01-01T00:00:00.000000Z",
        "notes": "notes c",
    }

    # Act
    resp = client.post("/exclusions/", json=data)

    print(resp.get_json())
    # Assert
    assert resp.status_code == 201

    exclusion = db.session.query(Exclusion).first()
    assert exclusion.application_technical_control_id == 33
    assert exclusion.summary == data["summary"]
    assert exclusion.mitigation == data["mitigation"]
    assert exclusion.probability == data["probability"]
    assert exclusion.impact == data["impact"]
    assert exclusion.is_limited_exclusion == data["isLimitedExclusion"]
    assert exclusion.end_date == datetime(2022, 1, 1, 0, 0)
    assert exclusion.notes == data["notes"]

    assert len(exclusion.resources) == 2
    assert exclusion.resources[0].reference == "res-c"
    assert exclusion.resources[1].reference == "res-d"
    assert exclusion.resources[0].exclusion_state == ExclusionState.PENDING
    assert exclusion.resources[1].exclusion_state == ExclusionState.PENDING
    assert exclusion.resources[0].exclusion_id == exclusion.id
    assert exclusion.resources[1].exclusion_id == exclusion.id


def test_exclusions_post_ok_for_existing_resources(client):
    """
    Given: An empty exclusions colllection, linked app controls, existing resources
    When: When the api is called with an exclusion request
    Then: The exclusions request is persisted & linked to existing resources, 201 status
    """
    # Arrange
    MonitoredResourceFactory(
        application_technical_control_id=33,
        reference="res-a",
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
    )
    MonitoredResourceFactory(
        application_technical_control_id=33,
        reference="res-b",
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
    )

    data = {
        "applicationTechnicalControlId": 33,
        "summary": "sum a",
        "mitigation": "mit b",
        "probability": 1,
        "impact": 2,
        "resources": ["res-a", "res-b"],
        "isLimitedExclusion": True,
        "endDate": "2022-01-01T00:00:00.000000Z",
        "notes": "notes c",
    }

    # Act
    resp = client.post("/exclusions/", json=data)

    print(resp.get_json())
    # Assert
    assert resp.status_code == 201

    exclusion = db.session.query(Exclusion).first()
    assert exclusion.application_technical_control_id == 33
    assert exclusion.summary == data["summary"]
    assert exclusion.mitigation == data["mitigation"]
    assert exclusion.probability == data["probability"]
    assert exclusion.impact == data["impact"]
    assert exclusion.is_limited_exclusion == data["isLimitedExclusion"]
    assert exclusion.end_date == datetime(2022, 1, 1, 0, 0)
    assert exclusion.notes == data["notes"]

    assert len(exclusion.resources) == 2
    assert exclusion.resources[0].reference == "res-a"
    assert exclusion.resources[1].reference == "res-b"
    assert exclusion.resources[0].exclusion_state == ExclusionState.PENDING
    assert exclusion.resources[1].exclusion_state == ExclusionState.PENDING
    assert exclusion.resources[0].exclusion_id == exclusion.id
    assert exclusion.resources[1].exclusion_id == exclusion.id


def test_exclusions_bad_request_for_missing_app_tech_control(client):
    """
    Given: An empty exclusions colllection, unlinked app/controls
    When: When the api is called with an exclusion request for missing app tech control
    Then: 404, no persistance
    """
    # Arrange

    data = {
        "applicationTechnicalControlId": 999,
        "summary": "sum a",
        "mitigation": "mit b",
        "probability": 1,
        "impact": 2,
        "resources": ["res-a", "res-b"],
        "isLimitedExclusion": True,
        "endDate": "2022-01-01T00:00:00.000Z",
        "notes": "notes c",
    }

    # Act
    resp = client.post("/exclusions/", json=data)

    # Assert
    assert resp.status_code == 400
    assert len(db.session.query(Exclusion).all()) == 0


def test_exclusions_post_bad_request_for_duplicate_resources(client):
    """
    Given: An existing exclusion in the db
    When: When the api is called with an exclusion request for pre existing resources
    Then: 404, no persistance
    """
    # Arrange

    ExclusionFactory(
        id=44,
        application_technical_control_id=33,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1),
        notes="nnn",
    )
    MonitoredResourceFactory(
        id=55,
        exclusion_id=44,
        reference="res-a",
        exclusion_state=ExclusionState.PENDING,
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=33,
    )

    data = {
        "applicationTechnicalControlId": 33,
        "summary": "sum a",
        "mitigation": "mit b",
        "probability": 1,
        "impact": 2,
        "resources": ["res-a", "res-b"],
        "isLimitedExclusion": True,
        "endDate": "2022-01-01 00:00:00.000",
        "notes": "notes c",
    }

    # Act
    resp = client.post("/exclusions/", json=data)

    # Assert
    assert resp.status_code == 400

    assert len(db.session.query(Exclusion).all()) == 1
    assert len(db.session.query(MonitoredResource).all()) == 1


def test_exclusions_post_ok_for_different_resources_resources(client):
    """
    Given: An existing exclusion in the db
    When: When the api is called with an exclusion request for non-existing resources
    Then: 201, new exclusion created
    """
    # Arrange

    ExclusionFactory(
        id=44,
        application_technical_control_id=33,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1),
        notes="nnn",
    )
    MonitoredResourceFactory(
        id=55,
        exclusion_id=44,
        reference="res-a",
        exclusion_state=ExclusionState.PENDING,
        monitoring_state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=33,
    )

    data = {
        "applicationTechnicalControlId": 33,
        "summary": "sum a",
        "mitigation": "mit b",
        "probability": 1,
        "impact": 2,
        "resources": ["res-b", "res-c"],
        "isLimitedExclusion": True,
        "endDate": "2022-01-01T00:00:00.000000Z",
        "notes": "notes c",
    }

    # Act
    resp = client.post("/exclusions/", json=data)

    # Assert
    assert resp.status_code == 201

    assert len(db.session.query(Exclusion).all()) == 2
    assert len(db.session.query(MonitoredResource).all()) == 3

    exclusion = db.session.query(Exclusion).filter(Exclusion.id != 44).first()
    assert exclusion.application_technical_control_id == 33
    assert exclusion.summary == data["summary"]
    assert exclusion.mitigation == data["mitigation"]
    assert exclusion.probability == data["probability"]
    assert exclusion.impact == data["impact"]
    assert exclusion.is_limited_exclusion == data["isLimitedExclusion"]
    assert exclusion.end_date == datetime(2022, 1, 1, 0, 0)
    assert exclusion.notes == data["notes"]


def test_exclusions_get_returns_correct_response(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to get exclusions by system
    Then: 200, exclusions returned
    """
    # Arrange
    add_get_items_to_db()

    # Act
    resp = client.get("/systems/1/exclusion-resources/")

    # Assert
    data = resp.get_json()

    assert resp.status_code == 200
    assert len(data) == 1
    item = data[0]
    assert item["id"] == 55
    assert item["technicalControlReference"] == "control_a"
    assert item["reference"] == "res-a"
    assert item["state"] == "PENDING"

    assert len(item["applicationReferences"]) == 1
    assert item["applicationReferences"][0]["type"] == "app-ref"
    assert item["applicationReferences"][0]["reference"] == "app-11"


def test_exclusions_get_filters_out_by_state(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to get exclusions by system
    Then: 200, exclusions returned
    """
    # Arrange
    add_get_items_to_db()

    # Act
    resp = client.get("/systems/2/exclusion-resources/?state=PENDING")

    # Assert
    data = resp.get_json()

    assert resp.status_code == 200
    assert len(data) == 1
    item = data[0]
    assert item["id"] == 56


def test_exclusions_get_handles_invalid_filter(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to get exclusions by system with a bad filter
    Then: 200, empty array returned
    """
    # Arrange
    add_get_items_to_db()

    # Act
    resp = client.get("/systems/2/exclusion-resources/?state=XXXXX")

    # Assert
    data = resp.get_json()

    assert resp.status_code == 200
    assert len(data) == 0


def test_exclusion_resources_put_bad_request_for_id_mismatch(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to update an exclusion resource with url & payload id mismatch
    Then: 400, no data changed
    """
    # Arrange
    add_get_items_to_db()

    data = {
        "id": 55,
        "technicalControlReference": "control_a",
        "reference": "res-a",
        "state": "ACTIVE",
    }

    # Act
    resp = client.put("/exclusion-resources/999/", json=data)

    # Assert
    assert resp.status_code == 400

    item = db.session.query(MonitoredResource).get(55)
    assert item.exclusion_state == ExclusionState.PENDING


def test_exclusion_resources_put_conflict_for_invalid_exclusion(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to update an exclusion which does not yet exist
    Then: 409 (conflict), no data changed
    """
    # Arrange
    add_get_items_to_db()

    data = {
        "id": 999,
        "technicalControlReference": "control_a",
        "reference": "res-a",
        "state": "ACTIVE",
    }

    # Act
    resp = client.put("/exclusion-resources/999/", json=data)

    # Assert
    assert resp.status_code == 409

    item = db.session.query(MonitoredResource).get(55)
    assert item.exclusion_state == ExclusionState.PENDING


def test_exclusion_resources_put_updates_record(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to get exclusions by system with a bad filter
    Then: 200, empty array returned
    """
    # Arrange
    add_get_items_to_db()

    data = {
        "id": 55,
        "technicalControlReference": "control_a",
        "reference": "res-a",
        "state": "ACTIVE",
    }

    # Act
    resp = client.put("/exclusion-resources/55/", json=data)

    # Assert
    assert resp.status_code == 204

    item = db.session.query(MonitoredResource).get(55)
    assert item.exclusion_state == ExclusionState.ACTIVE


def test_exclusion_resources_put_updates_record_with_sparse_response(client):
    """
    Given: Existing exclusion & resources in the db
    When: When the api is called to get exclusions by system with a bad filter
    Then: 200, empty array returned
    """
    # Arrange
    add_get_items_to_db()

    data = {
        "id": 55,
        "state": "ACTIVE",
    }

    # Act
    resp = client.put("/exclusion-resources/55/", json=data)

    # Assert
    assert resp.status_code == 204

    item = db.session.query(MonitoredResource).get(55)
    assert item.exclusion_state == ExclusionState.ACTIVE
