from datetime import datetime, timezone
from pprint import pprint
from airview_api.services import aggregation_service
from tests.factories import *
from tests.common import client
from airview_api.models import (
    Application,
    ApplicationTechnicalControl,
    MonitoredResource,
    TechnicalControlSeverity,
    ExclusionState,
    MonitoredResourceState,
    TechnicalControlType,
)


def setup():
    reset_factories()


def _prepare_aggregation_mock_data():
    SystemFactory(id=1, name="one", stage="build")
    EnvironmentFactory(id=1, abbreviation="DEV", name="aaa")
    EnvironmentFactory(id=2, abbreviation="PRD", name="bbb")
    ApplicationTypeFactory(id=1)
    ApplicationFactory(id=1, application_type_id=1)
    ApplicationFactory(id=12, parent_id=1, name="svc 12", environment_id=2)
    ApplicationFactory(id=13, parent_id=1, name="svc 13", environment_id=1)
    ApplicationFactory(id=14, parent_id=None, name="svc 13", environment_id=2)
    TechnicalControlFactory(
        id=22,
        name="ctl1",
        reference="control_a",
        control_type=TechnicalControlType.SECURITY,
        system_id=1,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=23,
        name="ctl2",
        reference="control_b",
        control_type=TechnicalControlType.TASK,
        system_id=1,
        severity=TechnicalControlSeverity.LOW,
    )
    TechnicalControlFactory(
        id=24,
        name="ctl3",
        reference="control_c",
        control_type=TechnicalControlType.SECURITY,
        system_id=1,
        severity=TechnicalControlSeverity.MEDIUM,
    )
    ApplicationTechnicalControlFactory(
        id=33, application_id=12, technical_control_id=22
    )
    ApplicationTechnicalControlFactory(
        id=34, application_id=12, technical_control_id=23
    )
    ApplicationTechnicalControlFactory(
        id=35, application_id=13, technical_control_id=22
    )
    ApplicationTechnicalControlFactory(
        id=36, application_id=14, technical_control_id=22
    )
    ApplicationTechnicalControlFactory(
        id=37, application_id=14, technical_control_id=24
    )

    # ctl 1 - Latest but FIXED
    MonitoredResourceFactory(
        id=102,
        application_technical_control_id=33,
        reference="res-1",
        state=MonitoredResourceState.SUPPRESSED,
        last_seen=datetime(2, 1, 1, tzinfo=timezone.utc),
        last_modified=datetime(2, 1, 1, tzinfo=timezone.utc),
    )
    # ctl 1 -Second resource
    MonitoredResourceFactory(
        id=103,
        application_technical_control_id=33,
        reference="res-2",
        state=MonitoredResourceState.FLAGGED,
        last_seen=datetime(3, 1, 1, tzinfo=timezone.utc),
        last_modified=datetime(3, 1, 1, tzinfo=timezone.utc),
    )
    # ctl2 - Different control
    MonitoredResourceFactory(
        id=104,
        application_technical_control_id=34,
        reference="res-3",
        state=MonitoredResourceState.FLAGGED,
        last_seen=datetime(4, 1, 1, tzinfo=timezone.utc),
        last_modified=datetime(4, 1, 1, tzinfo=timezone.utc),
    )
    # Ctl1 via different app
    MonitoredResourceFactory(
        id=105,
        application_technical_control_id=35,
        reference="res-4",
        state=MonitoredResourceState.FLAGGED,
        last_seen=datetime(5, 1, 1, tzinfo=timezone.utc),
        last_modified=datetime(5, 1, 1, tzinfo=timezone.utc),
    )
    # Unrelated data
    MonitoredResourceFactory(
        id=106,
        application_technical_control_id=36,
        reference="res-1-x",
        state=MonitoredResourceState.FLAGGED,
        last_seen=datetime(6, 1, 1, tzinfo=timezone.utc),
        last_modified=datetime(6, 1, 1, tzinfo=timezone.utc),
    )
    MonitoredResourceFactory(
        id=107,
        application_technical_control_id=37,
        reference="res-1-x",
        state=MonitoredResourceState.FLAGGED,
        last_seen=datetime(6, 1, 1, tzinfo=timezone.utc),
        last_modified=datetime(6, 1, 1, tzinfo=timezone.utc),
    )
    # Items not created until something is invoked, probably because of underlying raw query
    Application.query.all()


def _prepare_additional_data():  # Add additional exemptions
    MonitoredResourceFactory(
        id=108,
        application_technical_control_id=37,
        reference="res-1-other-2",
        state=MonitoredResourceState.SUPPRESSED,
        last_modified=datetime(6, 1, 1, tzinfo=timezone.utc),
        last_seen=datetime(6, 1, 1, tzinfo=timezone.utc),
    )

    MonitoredResourceFactory(
        id=109,
        application_technical_control_id=37,
        reference="res-1-other-3",
        state=MonitoredResourceState.SUPPRESSED,
        last_modified=datetime(6, 1, 1, tzinfo=timezone.utc),
        last_seen=datetime(6, 1, 1, tzinfo=timezone.utc),
    )
    ExclusionFactory(
        id=44,
        application_technical_control_id=33,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1, tzinfo=timezone.utc),
        notes="nnn",
    )
    mr = MonitoredResource.query.get(103)
    mr.exclusion_id = 44
    mr.exclusion_state = ExclusionState.ACTIVE
    Application.query.all()


def test_get_control_status_aggregation(client):
    """
    Given: A populated database of triggered resources
    When: When a request is made to list the triggered resources by application
    Then: The triggered resource information is returned. 200 status
    """
    # Arrange
    _prepare_aggregation_mock_data()
    # Act
    resp = client.get("/applications/1/control-statuses")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    expected = [
        {
            "id": 33,
            "controlType": "security",
            "severity": "high",
            "name": "ctl1",
            "systemName": "one",
            "systemStage": "build",
            "environment": "PRD",
            "application": "svc 12",
            "resources": [{"id": 103, "name": "res-2", "state": "NONE"}],
            "raisedDateTime": "0003-01-01T00:00:00",
            "tickets": [],
        },
        {
            "id": 35,
            "controlType": "security",
            "severity": "high",
            "name": "ctl1",
            "systemName": "one",
            "systemStage": "build",
            "environment": "DEV",
            "application": "svc 13",
            "resources": [{"id": 105, "name": "res-4", "state": "NONE"}],
            "raisedDateTime": "0005-01-01T00:00:00",
            "tickets": [],
        },
        {
            "id": 34,
            "controlType": "security",
            "severity": "low",
            "systemName": "one",
            "systemStage": "build",
            "name": "ctl2",
            "environment": "PRD",
            "application": "svc 12",
            "resources": [{"id": 104, "name": "res-3", "state": "NONE"}],
            "raisedDateTime": "0004-01-01T00:00:00",
            "tickets": [],
        },
    ]
    assert data == expected


def test_get_control_status_aggregation_removes_active_exclusions(client):
    """
    Given: A populated database of triggered resources. 1 excluded resource
    When: When a request is made to list the triggered resources by application
    Then: The triggered resource information is returned. 200 status. Excluded resource not in response
    """
    # Arrange
    _prepare_aggregation_mock_data()
    ExclusionFactory(
        id=44,
        application_technical_control_id=33,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1, tzinfo=timezone.utc),
        notes="nnn",
    )

    mr = MonitoredResource.query.get(103)
    mr.exclusion_id = 44
    mr.exclusion_state = ExclusionState.ACTIVE
    # ExclusionResourceFactory(
    # id=55, exclusion_id=44, reference="res-2", state=ExclusionState.ACTIVE
    # )
    Application.query.all()

    # Act
    resp = client.get("/applications/1/control-statuses")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    expected = [
        {
            "id": 35,
            "controlType": "security",
            "severity": "high",
            "name": "ctl1",
            "systemName": "one",
            "systemStage": "build",
            "environment": "DEV",
            "application": "svc 13",
            "resources": [{"id": 105, "name": "res-4", "state": "NONE"}],
            "raisedDateTime": "0005-01-01T00:00:00",
            "tickets": [],
        },
        {
            "id": 34,
            "controlType": "security",
            "severity": "low",
            "name": "ctl2",
            "systemName": "one",
            "systemStage": "build",
            "environment": "PRD",
            "application": "svc 12",
            "resources": [{"id": 104, "name": "res-3", "state": "NONE"}],
            "raisedDateTime": "0004-01-01T00:00:00",
            "tickets": [],
        },
    ]
    assert data == expected


def test_get_control_status_aggregation_empty_result_for_unfound_app(client):
    """
    Given: A populated database of triggered resources
    When: When a request is made to list the triggered resources by application using an invalid id
    Then: An empty list is returned. 200 status
    """
    # Arrange
    _prepare_aggregation_mock_data()
    # Act
    resp = client.get("/applications/999/control-statuses")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 0


def test_get_control_status_aggregation_handles_no_children(client):
    """
    Given: A populated database of triggered resources
    When: When a request is made to list the triggered resources by application using an invalid id
    Then: An empty list is returned. 200 status
    """
    # Arrange
    _prepare_aggregation_mock_data()
    # Act
    resp = client.get("/applications/12/control-statuses")

    # Assert
    data = resp.get_json()

    expected = [
        {
            "id": 33,
            "controlType": "security",
            "severity": "high",
            "name": "ctl1",
            "systemName": "one",
            "systemStage": "build",
            "environment": "PRD",
            "application": "svc 12",
            "resources": [{"id": 103, "name": "res-2", "state": "NONE"}],
            "raisedDateTime": "0003-01-01T00:00:00",
            "tickets": [],
        },
        {
            "id": 34,
            "controlType": "security",
            "severity": "low",
            "name": "ctl2",
            "systemName": "one",
            "systemStage": "build",
            "environment": "PRD",
            "application": "svc 12",
            "resources": [{"id": 104, "name": "res-3", "state": "NONE"}],
            "raisedDateTime": "0004-01-01T00:00:00",
            "tickets": [],
        },
    ]
    assert resp.status_code == 200
    assert data == expected


def test_get_application_compliance_overview(client):
    """
    Given: A populated database of triggered resources
    When: When a request is made to list the triggered resources by application using an invalid id
    Then: An aggregated response of the data is returned. 200 status
    """
    # Arrange
    _prepare_aggregation_mock_data()
    # Add additional data
    _prepare_additional_data()

    # aggregation_service.get_application_compliance_overview()
    # Act
    resp = client.get("/application-statuses/")

    # Assert
    data = resp.get_json()

    expected = [
        {
            "id": 1,
            "applicationName": "App 0",
            "environments": [
                {
                    "environment": "aaa",
                    "high": 1,
                    "medium": 0,
                    "low": 0,
                    "exemptControls": 0,
                    "failedControls": 1,
                    "totalControls": 1,
                },
                {
                    "environment": "bbb",
                    "high": 0,
                    "medium": 0,
                    "low": 1,
                    "exemptControls": 1,
                    "failedControls": 1,
                    "totalControls": 2,
                },
            ],
        },
        {
            "id": 14,
            "applicationName": "svc 13",
            "environments": [
                {
                    "environment": "bbb",
                    "high": 1,
                    "medium": 1,
                    "low": 0,
                    "exemptControls": 0,
                    "failedControls": 2,
                    "totalControls": 2,
                }
            ],
        },
    ]

    assert expected == data


def test_get_application_control_overview(client):
    """
    Given: A populated database of triggered resources
    When: When a request is made to list the control data
    Then: An aggregated response of the data is returned. 200 status
    """
    # Arrange
    _prepare_aggregation_mock_data()
    # Add additional data
    _prepare_additional_data()

    # Act
    resp = client.get("/applications/1/control-overviews?qualityModel=SECURITY")

    # Assert
    data = resp.get_json()
    expected = [
        {
            "applied": 3,
            "controlType": "SECURITY",
            "exempt": 1,
            "id": 22,
            "severity": "HIGH",
            "name": "ctl1",
            "systemName": "one",
            "systemStage": "build",
        },
        {
            "applied": 1,
            "controlType": "TASK",
            "exempt": 0,
            "id": 23,
            "severity": "LOW",
            "name": "ctl2",
            "systemName": "one",
            "systemStage": "build",
        },
    ]

    assert expected == data


def test_get_application_control_overview_hides_parents(client):
    """
    Given: A populated database of triggered resources
    When: When a request is made to list the control data for a sub-application
    Then: An aggregated response of the data is returned. 200 status
    """
    # Arrange
    _prepare_aggregation_mock_data()
    # Add additional data
    _prepare_additional_data()

    # Act
    resp = client.get("/applications/13/control-overviews?qualityModel=SECURITY")

    # Assert
    data = resp.get_json()
    expected = [
        {
            "applied": 1,
            "controlType": "SECURITY",
            "exempt": 0,
            "id": 22,
            "name": "ctl1",
            "severity": "HIGH",
            "systemName": "one",
            "systemStage": "build",
        }
    ]
    assert expected == data
