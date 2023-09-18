from datetime import datetime, timedelta
from airview_api.models import ControlSeverity, QualityModel, ResourceTypeControl
from tests.common import client
from tests.factories import *
import pytest
from pprint import pprint


def setup():
    reset_factories()

    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ResourceTypeFactory(
        id=20, name="res type one", reference="res-type-1", service_id=10
    )
    ResourceTypeFactory(
        id=21, name="res type two", reference="res-type-2", service_id=10
    )
    ControlFactory(
        id=2, name="testcontrol", quality_model=QualityModel.SECURITY, severity=ControlSeverity.LOW,
    )

    db.session.commit()


def test_resource_type_controls_post_ok(client):
    """
    Given: Services, Resources types and Controls pre exist in the db
    When: When a call is made to link a resource type to a control
    Then: The link is created via the resource type control item
    """

    # Act
    resp = client.post(
        "/resource-types-controls/",
        json={
            "controlId": 2,
            "resourceTypeId": 21,
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 1

    # Assert persistance
    items = db.session.query(ResourceTypeControl).all()
    assert len(items) == 1
    assert items[0].resource_type_id == 21
    assert items[0].control_id == 2


def test_resources_get_single_by_control_and_resource_type(client):
    """
    Given: An existing resource type in the collection
    When: When a call is made to get it by its reference
    Then: The resource is mapped correctly, 200 status
    """
    # Arrange
    ResourceTypeControlFactory(
        id=2,
        resource_type_id=21,
        control_id=2
    )

    # Act
    resp = client.get(
        "/resource-types-controls/?controlId=2&resourceTypeId=21",
    )
    # Assert
    assert resp.status_code == 200

    # Assert Response
    data = resp.get_json()

    assert data["id"] == 2


def test_resources_get_single_not_found(client):
    """
    Given: An existing resource in the collection
    When: When a call is made to get a resource which is not present by its unique keys
    Then: 404 status
    """
    # Arrange
    # Act
    resp = client.get(
        "/resource-types-controls/?controlId=3&resourceTypeId=2",
    )
    # Assert
    assert resp.status_code == 404
