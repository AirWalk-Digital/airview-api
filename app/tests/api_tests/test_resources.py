from datetime import datetime
from airview_api.models import TechnicalControlSeverity, Resource, ApplicationType
from tests.common import client
from tests.factories import *


def setup():
    reset_factories()


def test_resources_post_ok(client):
    """
    Given: Resources exist for same app with different reference & different app with same reference
    When: When a call is made to persist a resource
    Then: The item is persisted and the id populated
    """
    # Arrange
    ApplicationFactory(
        id=1, name="App One", application_type=ApplicationType.APPLICATION_SERVICE
    )
    ApplicationFactory(
        id=2, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )

    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    ResourceFactory(
        name="Res AAA",
        reference="same_app_ref",
        service_id=10,
        application_id=1,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )

    ResourceFactory(
        name="Res BBB",
        reference="ref_1",
        service_id=10,
        application_id=2,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/resources/",
        json={
            "name": "Res One",
            "reference": "res_1",
            "serviceId": 10,
            "applicationId": 1,
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    print(data)
    assert data["name"] == "Res One"
    assert data["reference"] == "res_1"
    assert data["applicationId"] == 1
    assert data["serviceId"] == 10

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 3
    assert items[2].id == 3
    assert items[2].name == "Res One"
    assert items[2].reference == "res_1"
    assert items[2].application_id == 1
    assert items[2].service_id == 10


def test_resources_post_handle_duplicate_error(client):
    """
    Given: An existing resource with same reference and app in db
    When: When a call is made to persist a resource
    Then: The item is rejected with 409
    """
    # Arrange
    ApplicationFactory(
        id=1,
        name="App One",
        application_type=ApplicationType.APPLICATION_SERVICE,
    )

    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")
    ResourceFactory(
        name="Res One",
        reference="res_1",
        service_id=10,
        application_id=1,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/resources/",
        json={
            "name": "Res One",
            "reference": "res_1",
            "serviceId": 10,
            "applicationId": 1,
        },
    )
    # Assert
    assert resp.status_code == 400

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 1
