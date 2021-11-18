from datetime import datetime
from pprint import pprint
from tests.factories import *
from tests.common import client
from airview_api.models import (
    Application,
    ApplicationTechnicalControl,
    MonitoredResource,
    TechnicalControlSeverity,
    TechnicalControlType,
)


def setup():
    reset_factories()


def test_technical_control_get_single_ok(client):
    """
    Given: A collection of technical controls exist in the database
    When: When the api is called with an id
    Then: The corrisponding technical control is returned with status 200
    """
    # Arrange
    SystemFactory(id=2)
    TechnicalControlFactory(
        id=701,
        reference="1",
        name="one",
        control_type=TechnicalControlType.SECURITY,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=702,
        reference="2",
        name="two",
        control_type=TechnicalControlType.OPERATIONAL,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=703,
        reference="3",
        name="three",
        control_type=TechnicalControlType.SECURITY,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )

    # Act
    resp = client.get("/technical-controls/702")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["id"] == 702
    assert data["name"] == "two"
    assert data["controlType"] == "OPERATIONAL"
    assert data["systemId"] == 2


def test_technical_control_get_single_not_found(client):
    """
    Given: A collection of technical controls exists in the database
    When: When the id does not exit in the database
    Then: Status 404 is returned with an empty response
    """
    # Arrange
    SystemFactory(id=2)
    TechnicalControlFactory(
        id=701,
        reference="1",
        name="one",
        control_type=TechnicalControlType.SECURITY,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=702,
        reference="2",
        name="two",
        control_type=TechnicalControlType.SECURITY,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=703,
        reference="3",
        name="three",
        control_type=TechnicalControlType.SECURITY,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )

    # Act
    resp = client.get("/technical-controls/710")

    # Assert
    assert resp.status_code == 404


def test_technical_controls_post_reject_bad_reference(client):
    """
    Given: An empty technicalContols table
    When: When a technical control definition is posted to the api with url escaped chars in ref
    Then: 402 status, no data stored
    """
    # Arrange
    SystemFactory(id=2)
    input_data = {
        "name": "Ctrl1",
        "reference": "bad$reference",
        "controlType": "TASK",
        "systemId": 2,
        "severity": "LOW",
    }

    # Act
    resp = client.post(
        "/technical-controls/",
        json=input_data,
    )

    # Assert
    assert resp.status_code == 422
    persisted = TechnicalControl.query.all()
    assert len(persisted) == 0


def test_technical_controls_post_ok_new(client):
    """
    Given: An empty technicalContols table
    When: When a correctly formed technical control definition is posted to the api
    Then: The technical control is returned with status 200 and stored in db
    """
    # Arrange
    SystemFactory(id=2)
    input_data = {
        "name": "Ctrl1",
        "reference": "ctl_id_one",
        "controlType": "TASK",
        "systemId": 2,
        "severity": "LOW",
        "qualityModel": "SECURITY",
    }

    # Act
    resp = client.post(
        "/technical-controls/",
        json=input_data,
    )

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["name"] == input_data["name"]
    assert data["reference"] == input_data["reference"]
    assert data["controlType"] == input_data["controlType"]
    assert data["systemId"] == input_data["systemId"]
    assert data["severity"] == input_data["severity"]

    persisted = TechnicalControl.query.all()
    assert len(persisted) == 1
    assert persisted[0].name == input_data["name"]
    assert persisted[0].reference == input_data["reference"]
    assert persisted[0].control_type == TechnicalControlType.TASK
    assert persisted[0].system_id == input_data["systemId"]
    assert persisted[0].severity == TechnicalControlSeverity.LOW


def test_technical_controls_post_ok_sets_defaut_severity(client):
    """
    Given: An empty technicalContols table
    When: When a correctly formed technical control definition is posted to the api with missing severtiy
    Then: The technical control is returned with status 200 and stored in db, severity defaults to HIGh
    """
    # Arrange
    SystemFactory(id=2)
    input_data = {
        "name": "Ctrl1",
        "reference": "ctl_id_one",
        "controlType": "TASK",
        "systemId": 2,
        "qualityModel": "SECURITY",
    }

    # Act
    resp = client.post(
        "/technical-controls/",
        json=input_data,
    )

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["name"] == input_data["name"]
    assert data["reference"] == input_data["reference"]
    assert data["controlType"] == input_data["controlType"]
    assert data["systemId"] == 2
    assert data["severity"] == "HIGH"
    assert data["qualityModel"] == "SECURITY"

    persisted = TechnicalControl.query.all()
    assert len(persisted) == 1
    assert persisted[0].name == input_data["name"]
    assert persisted[0].reference == input_data["reference"]
    assert persisted[0].control_type == TechnicalControlType.TASK
    assert persisted[0].system_id == input_data["systemId"]
    assert persisted[0].severity == TechnicalControlSeverity.HIGH


def test_technical_controls_post_bad_request_for_existing(client):
    """
    Given: reference 123 exists as a technical control already
    When: When a correctly formed technical control definition with reference 123 is posted to the api
    Then: A 400 error is returned. No additional record is persisted to the db
    """
    # Arrange
    TechnicalControlFactory(
        reference="123", system_id=2, severity=TechnicalControlSeverity.HIGH
    )
    input_data = {
        "name": "Ctrl1",
        "reference": "123",
        "controlType": "TASK",
        "systemId": 1,
        "severity": "HIGH",
        "qualityModel": "SECURITY",
    }

    # Act
    resp = client.post(
        "/technical-controls/",
        json=input_data,
    )

    # Assert
    assert b"Unique Constraint Error" in resp.data
    assert resp.status_code == 400


def test_technical_controls_get_with_filter(client):
    """
    Given: A linked application and system
    When: When a call is made to the get the application by its link
    Then: An array of application is returned with status 200
    """
    # Arrange
    SystemFactory(id=11, name="sysabc")
    SystemFactory(id=12, name="aaasysabc")

    TechnicalControlFactory(
        id=1,
        name="ctrl1",
        reference="ctrl_abc",
        control_type=TechnicalControlType.SECURITY,
        system_id=11,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=2,
        name="ctrl1",
        reference="ctrl_abc",
        control_type=TechnicalControlType.SECURITY,
        system_id=12,
        severity=TechnicalControlSeverity.HIGH,
    )
    TechnicalControlFactory(
        id=3,
        name="ctrl1",
        reference="xxx-ctrl_abc",
        control_type=TechnicalControlType.SECURITY,
        system_id=11,
        severity=TechnicalControlSeverity.HIGH,
    )

    # Act
    resp = client.get("/technical-controls/?systemId=11&reference=ctrl_abc")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["name"] == "ctrl1"
    assert data[0]["reference"] == "ctrl_abc"
    assert data[0]["controlType"] == "SECURITY"
