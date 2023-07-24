from datetime import datetime, timedelta
from airview_api.models import Resource, ApplicationType
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

    db.session.commit()


def test_resources_post_ok(client):
    """
    Given: Services pre exist in the db
    When: When a call is made to persist a resource type with a unique reference
    Then: The item is persisted and the id populated
    """

    # Act
    resp = client.post(
        "/resource-types/",
        json={
            "name": "Type One",
            "reference": "type_1",
            "serviceId": 10,
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    print(data)
    assert data["name"] == "Type One"
    assert data["reference"] == "type_1"
    assert data["serviceId"] == 10

    # Assert persistance
    items = db.session.query(ResourceType).all()
    pprint(items)
    assert len(items) == 3
    assert items[2].name == "Type One"
    assert items[2].reference == "type_1"
    assert items[2].service_id == 10


def test_resources_post_handle_duplicate_error(client):
    """
    Given: An existing resource type with same reference
    When: When a call is made to persist a resource type
    Then: The item is rejected with 409
    """
    # Arrange
    ResourceTypeFactory(
        name="Duplicate",
        reference="type_1",
        service_id=10,
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/resource-types/",
        json={
            "name": "Type One",
            "reference": "type_1",
            "serviceId": 10,
        },
    )
    # Assert
    assert resp.status_code == 409

    # Assert persistance
    items = db.session.query(ResourceType).all()
    assert len(items) == 3


def test_resources_get_single(client):
    """
    Given: An existing resource type in the collection
    When: When a call is made to get it by its reference
    Then: The resource is mapped correctly, 200 status
    """
    # Arrange
    ResourceTypeFactory(
        id=99,
        name="Existing",
        reference="type_1",
        service_id=10,
    )

    # Act
    resp = client.get(
        "/resource-types/?reference=type_1",
    )
    # Assert
    assert resp.status_code == 200

    # Assert Response
    data = resp.get_json()

    assert data["id"] == 99
    assert data["name"] == "Existing"
    assert data["reference"] == "type_1"
    assert data["serviceId"] == 10


def test_resources_get_single_not_found(client):
    """
    Given: An existing resource in the collection
    When: When a call is made to get a resource which is not present by its unique keys
    Then: 404 status
    """
    # Arrange
    # Act
    resp = client.get(
        "/resource-types/?reference=type_1",
    )
    # Assert
    assert resp.status_code == 404
