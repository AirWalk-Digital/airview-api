from airview_api.models import TechnicalControlSeverity
from tests.common import client
from tests.factories import *


def test_systems_post_ok(client):
    """
    Given: No systems in the db
    When: When a call is made to persist a system
    Then: The item is persisted and the id populated
    """
    # Arrange

    # Act
    resp = client.post("/systems/", json={"name": "System One", "stage": "stg"})
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "System One"
    assert data["stage"] == "stg"
    assert data["id"] == 1

    # Assert persistance
    items = db.session.query(System).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "System One"
    assert items[0].stage == "stg"


def test_systems_post_handle_duplicate_error(client):
    """
    Given: An existing system with same name in db
    When: When a call is made to persist a system
    Then: The item is rejected with 409
    """
    # Arrange
    SystemFactory(name="System One")
    db.session.commit()

    # Act
    resp = client.post("/systems/", json={"name": "System One", "stage": "stg"})
    # Assert
    assert resp.status_code == 400

    # Assert persistance
    items = db.session.query(System).all()
    assert len(items) == 1


def test_systems_get_by_reference(client):
    """
    Given: An existing system in db
    When: When a call is made to get it by it's reference
    Then: The item is returned with 200 status
    """
    # Arrange
    SystemFactory(id=1, name="System One", stage="tmp")
    db.session.commit()

    # Act
    resp = client.get("/systems/?name=System One")
    # Assert
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["id"] == 1
    assert data["name"] == "System One"
    assert data["stage"] == "tmp"


def test_systems_get_by_reference_not_found(client):
    """
    Given: An existing system in db
    When: When a call is made to get a different name
    Then: 404 status
    """
    # Arrange
    SystemFactory(id=1, name="System One", stage="tmp")
    db.session.commit()

    # Act
    resp = client.get("/systems/?name=System Two")
    # Assert
    assert resp.status_code == 404
