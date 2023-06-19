from airview_api.models import Service, ServiceType
from tests.common import client
from tests.factories import *


def setup():
    reset_factories()


def test_services_post_ok(client):
    """
    Given: No services in the db
    When: When a call is made to persist a service
    Then: The item is persisted and the id populated
    """
    # Arrange

    # Act
    resp = client.post(
        "/services/",
        json={"name": "Service One", "reference": "ref_1", "type": "NETWORK"},
    )

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Service One"
    assert data["type"] == "NETWORK"
    assert data["reference"] == "ref_1"
    assert data["id"] == 1

    # Assert persistance
    items = db.session.query(Service).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "Service One"
    assert items[0].type == ServiceType.NETWORK
    assert items[0].reference == "ref_1"


def test_services_post_handle_duplicate_error(client):
    """
    Given: An existing service with same referece in db
    When: When a call is made to persist a service
    Then: The item is rejected with 409
    """
    # Arrange
    ServiceFactory(id=1, name="Service One", reference="ref_1", type="NETWORK")
    db.session.commit()

    # Act
    resp = client.post(
        "/services/",
        json={"name": "Service Two", "reference": "ref_1", "type": "NETWORK"},
    )
    # Assert
    assert resp.status_code == 400

    # Assert persistance
    items = db.session.query(Service).all()
    assert len(items) == 1


def test_services_get_all(client):
    """
    Given: An existing service in db
    When: When a call is made to get all
    Then: The item is returned with 200 status
    """
    # Arrange
    ServiceFactory(id=1, name="Service One", reference="ref_1", type="NETWORK")
    db.session.commit()

    # Act
    resp = client.get("/services/")
    # Assert
    assert resp.status_code == 200

    data = resp.get_json()
    assert len(data) == 1

    assert data[0]["id"] == 1
    assert data[0]["name"] == "Service One"
    assert data[0]["type"] == "NETWORK"
    assert data[0]["reference"] == "ref_1"
