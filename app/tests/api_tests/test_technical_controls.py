from datetime import datetime
from pprint import pprint
from tests.factories import *
from tests.common import client
from airview_api.models import (
    TechnicalControlAction,
    SystemStage,
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
    SystemFactory(id=2, stage=SystemStage.BUILD)
    TechnicalControlFactory(
        id=701,
        reference="1",
        name="one",
        system_id=2,
        control_action=TechnicalControlAction.INCIDENT,
    )
    TechnicalControlFactory(
        id=702,
        reference="2",
        name="two",
        system_id=2,
        is_blocking=True,
        ttl=10,
        control_action=TechnicalControlAction.LOG,
    )
    TechnicalControlFactory(
        id=703,
        reference="3",
        name="three",
        system_id=2,
        control_action=TechnicalControlAction.INCIDENT,
    )

    # Act
    resp = client.get("/technical-controls/702")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["id"] == 702
    assert data["name"] == "two"
    assert data["systemId"] == 2
    assert data["reference"] == "2"
    assert data["isBlocking"] == True
    assert data["ttl"] == 10
    assert data["controlAction"] == "LOG"


def test_technical_control_get_single_not_found(client):
    """
    Given: A collection of technical controls exists in the database
    When: When the id does not exit in the database
    Then: Status 404 is returned with an empty response
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    TechnicalControlFactory(
        id=701,
        reference="1",
        name="one",
        system_id=2,
        control_action=TechnicalControlAction.INCIDENT,
    )
    TechnicalControlFactory(
        id=702,
        reference="2",
        name="two",
        system_id=2,
        control_action=TechnicalControlAction.INCIDENT,
    )
    TechnicalControlFactory(
        id=703,
        reference="3",
        name="three",
        system_id=2,
        control_action=TechnicalControlAction.INCIDENT,
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
    SystemFactory(id=2, stage=SystemStage.BUILD)
    input_data = {
        "name": "Ctrl1",
        "reference": "bad$reference",
        "systemId": 2,
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
    Given: An tech control table with 1 control
    When: When a correctly formed technical control definition is posted to the api
    Then: The technical control is returned with status 200 and stored in db
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    TechnicalControlFactory(
        id=701,
        reference="1",
        name="one",
        system_id=2,
        control_action=TechnicalControlAction.INCIDENT,
    )

    input_data = {
        "name": "Ctrl1",
        "reference": "ctl_id_one",
        "systemId": 2,
        "ttl": 20,
        "isBlocking": True,
        "controlAction": "LOG",
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
    assert data["systemId"] == input_data["systemId"]
    assert data["ttl"] == input_data["ttl"]
    assert data["isBlocking"] == input_data["isBlocking"]
    assert data["controlAction"] == input_data["controlAction"]

    persisted = TechnicalControl.query.all()
    assert len(persisted) == 2
    assert persisted[1].name == input_data["name"]
    assert persisted[1].reference == input_data["reference"]
    assert persisted[1].system_id == input_data["systemId"]
    assert persisted[1].ttl == 20
    assert persisted[1].is_blocking == True
    assert persisted[1].control_action == TechnicalControlAction.LOG


def test_technical_controls_post_ok_sets_defaults(client):
    """
    Given: An empty technicalContols table
    When: When a correctly formed technical control definition is posted to the api with missing optional fields
    Then: The technical control is returned with status 200 and stored in db, optional fields take on default values
    """
    # Arrange
    SystemFactory(id=2, stage=SystemStage.BUILD)
    input_data = {
        "name": "Ctrl1",
        "reference": "ctl_id_one",
        "systemId": 2,
        "controlAction": "LOG",
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
    assert data["controlAction"] == input_data["controlAction"]
    assert data["systemId"] == 2
    # Assert defaults
    assert data["isBlocking"] == False
    assert data.get("ttl") is None

    persisted = TechnicalControl.query.all()
    assert len(persisted) == 1
    assert persisted[0].name == input_data["name"]
    assert persisted[0].reference == input_data["reference"]
    assert persisted[0].system_id == input_data["systemId"]
    assert persisted[0].control_action == TechnicalControlAction.LOG


def test_technical_controls_post_bad_request_for_existing(client):
    """
    Given: reference 123 exists as a technical control already
    When: When a correctly formed technical control definition with reference 123 is posted to the api
    Then: A 400 error is returned. No additional record is persisted to the db
    """
    # Arrange
    TechnicalControlFactory(reference="123", system_id=2)
    input_data = {
        "name": "Ctrl1",
        "reference": "123",
        "systemId": 1,
        "controlAction": "LOG",
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
    SystemFactory(id=11, name="sysabc", stage=SystemStage.BUILD)
    SystemFactory(id=12, name="aaasysabc", stage=SystemStage.BUILD)

    TechnicalControlFactory(
        id=1,
        name="ctrl1",
        reference="ctrl_abc",
        system_id=11,
        control_action=TechnicalControlAction.TASK,
    )
    TechnicalControlFactory(
        id=2,
        name="ctrl1",
        reference="ctrl_abc",
        system_id=12,
        control_action=TechnicalControlAction.INCIDENT,
    )
    TechnicalControlFactory(
        id=3,
        name="ctrl1",
        reference="xxx-ctrl_abc",
        system_id=11,
        control_action=TechnicalControlAction.LOG,
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
    assert data[0]["controlAction"] == "TASK"
