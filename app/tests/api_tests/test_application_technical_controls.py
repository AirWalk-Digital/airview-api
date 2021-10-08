from datetime import datetime
from pprint import pprint
from tests.factories import *
from tests.common import client
import tests.common
from airview_api.models import (
    Application,
    ApplicationTechnicalControl,
    MonitoredResource,
    TechnicalControlSeverity,
)


def setup():
    reset_factories()


def test_application_technical_control_get_single_ok(client):
    """
    Given: A collection of application technical controls exist in the database
    When: When the api is called with correct uri
    Then: The corrisponding application technical control is returned with status 200
    """
    # Arrange
    SystemFactory(id=2)
    ApplicationTypeFactory(id=1)
    ApplicationFactory(id=1)
    ApplicationFactory(id=2)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_type_id=1,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=201, application_id=1, technical_control_id=101
    )
    ApplicationTechnicalControlFactory(
        id=202, application_id=2, technical_control_id=101
    )

    # Act
    resp = client.get(
        "/application-technical-controls/?applicationId=1&technicalControlId=101"
    )

    # Assert
    data = resp.get_json()
    pprint(data)
    assert resp.status_code == 200
    assert data["id"] == 201
    assert data["applicationId"] == 1
    assert data["technicalControlId"] == 101


def test_application_technical_control_not_found(client):
    """
    Given: A collection of application technical controls exist in the database
    When: When the api is called with non-existing identifiers
    Then: 404 status
    """
    # Arrange
    SystemFactory(id=2)
    ApplicationTypeFactory(id=1)
    ApplicationFactory(id=1)
    ApplicationFactory(id=2)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_type_id=1,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=201, application_id=1, technical_control_id=101
    )
    ApplicationTechnicalControlFactory(
        id=202, application_id=2, technical_control_id=101
    )

    # Act
    resp = client.get(
        "/application-technical-controls/?applicationId=999&technicalControlId=101"
    )

    # Assert
    assert resp.status_code == 404


def test_application_technical_control_post_ok(client):
    """
    Given: Unlinked apps and controls
    When: When the api is called to link them
    Then: 200 status, new object returned
    """
    # Arrange
    SystemFactory(id=2)
    ApplicationTypeFactory(id=1)
    ApplicationFactory(id=1)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_type_id=1,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )

    input_data = {"applicationId": 1, "technicalControlId": 101}
    # Act

    resp = client.post("/application-technical-controls/", json=input_data)

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["applicationId"] == 1
    assert data["technicalControlId"] == 101

    items = db.session.query(ApplicationTechnicalControl).all()
    assert len(items) == 1


def test_application_technical_control_post_conflict_when_exist(client):
    """
    Given: existing linked apps and controls
    When: When the api is called to link them
    Then: 200 status, new object returned
    """
    # Arrange
    SystemFactory(id=2)
    ApplicationTypeFactory(id=1)
    ApplicationFactory(id=1)
    TechnicalControlFactory(
        id=101,
        reference="1",
        name="one",
        control_type_id=1,
        system_id=2,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=201, application_id=1, technical_control_id=101
    )

    input_data = {"applicationId": 1, "technicalControlId": 101}
    # Act

    resp = client.post("/application-technical-controls/", json=input_data)

    # Assert
    assert resp.status_code == 409
