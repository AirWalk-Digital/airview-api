from datetime import datetime, timedelta
from airview_api.models import Resource, ApplicationType
from tests.common import client
from tests.factories import *
import pytest


def setup():
    reset_factories()
    EnvironmentFactory(id=1)
    ApplicationFactory(
        id=1, name="App One", application_type=ApplicationType.APPLICATION_SERVICE
    )
    ApplicationFactory(
        id=2, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=1)
    ApplicationEnvironmentFactory(id=2, application_id=2, environment_id=1)

    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")
    ServiceFactory(id=11, name="Service Two", reference="ref_2", type="NETWORK")

    ResourceTypeFactory(
        id=20, name="res type one", reference="res-type-1", service_id=10
    )
    ResourceTypeFactory(
        id=21, name="res type two", reference="res-type-2", service_id=10
    )


def test_resources_post_ok(client):
    """
    Given: Resources exist for same app with different reference & different app with same reference
    When: When a call is made to persist a resource
    Then: The item is persisted and the id populated
    """
    # Arrange
    ResourceFactory(
        name="Res AAA",
        reference="same_app_ref",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )

    ResourceFactory(
        name="Res BBB",
        reference="ref_1",
        resource_type_id=20,
        application_environment_id=2,
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
            "resourceTypeId": 20,
            "applicationEnvironmentId": 1,
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    print(data)
    assert data["name"] == "Res One"
    assert data["reference"] == "res_1"
    assert data["applicationEnvironmentId"] == 1
    assert data["resourceTypeId"] == 20

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 3
    assert items[2].id == 3
    assert items[2].name == "Res One"
    assert items[2].reference == "res_1"
    assert items[2].application_environment_id == 1
    assert items[2].resource_type_id == 20


def test_resources_post_handle_duplicate_error(client):
    """
    Given: An existing resource with same reference and app in db
    When: When a call is made to persist a resource
    Then: The item is rejected with 409
    """
    # Arrange
    ResourceFactory(
        name="Res One",
        reference="res_1",
        resource_type_id=20,
        application_environment_id=1,
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
            "resourceTypeId": 20,
            "applicationEnvironmentId": 1,
        },
    )
    # Assert
    assert resp.status_code == 400

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 1


def test_resources_put_creates_new(client):
    """
    Given: No existing resource in the collection
    When: When a call is made to update a resource
    Then: The item is updated and a 204 status returned
    """
    # Arrange

    time_now = datetime.utcnow()

    db.session.commit()

    # Act
    resp = client.put(
        "/resources/?applicationEnvironmentId=1&reference=res_1",
        json={
            "name": "Res One Update",
            "reference": "res_1",
            "resourceTypeId": 21,
            "applicationEnvironmentId": 1,
        },
    )
    # Assert
    assert resp.status_code == 204

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 1

    assert items[0].id == 1
    assert items[0].name == "Res One Update"
    assert items[0].reference == "res_1"
    assert items[0].application_environment_id == 1
    assert items[0].resource_type_id == 21
    assert items[0].last_seen > time_now
    assert items[0].last_modified > time_now


def test_resources_put_updates_existing(client):
    """
    Given: An existing resource in the collection
    When: When a call is made to update a resource
    Then: The item is updated and a 201 status returned
    """
    # Arrange
    time_now = datetime.utcnow()
    ResourceFactory(
        name="Res One",
        reference="res_1",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=time_now,
        last_seen=time_now,
    )

    db.session.commit()

    # Act
    resp = client.put(
        "/resources/?applicationEnvironmentId=1&reference=res_1",
        json={
            "name": "Res One Update",
            "reference": "res_1",
            "resourceTypeId": 21,
            "applicationEnvironmentId": 1,
        },
    )
    # Assert
    assert resp.status_code == 204

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 1

    assert items[0].id == 1
    assert items[0].name == "Res One Update"
    assert items[0].reference == "res_1"
    assert items[0].application_environment_id == 1
    assert items[0].resource_type_id == 21
    assert items[0].last_seen > time_now
    assert items[0].last_modified > time_now


def test_resources_put_does_not_change_modify_when_no_change(client):
    """
    Given: An existing resource in the collection
    When: When a call is made to update a resource but the resource is the same
    Then: The last updated date is updated, last modified is the same and a 204 status returned
    """
    # Arrange
    time_now = datetime.utcnow()
    ResourceFactory(
        name="Res One",
        reference="res_1",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=time_now,
        last_seen=time_now,
    )

    db.session.commit()

    # Act
    resp = client.put(
        "/resources/?applicationEnvironmentId=1&reference=res_1",
        json={
            "name": "Res One",
            "reference": "res_1",
            "resourceTypeId": 20,
            "applicationEnvironmentId": 1,
        },
    )
    # Assert
    assert resp.status_code == 204

    # Assert persistance
    items = db.session.query(Resource).all()
    assert len(items) == 1

    assert items[0].id == 1
    assert items[0].name == "Res One"
    assert items[0].reference == "res_1"
    assert items[0].application_environment_id == 1
    assert items[0].resource_type_id == 20
    assert items[0].last_seen > time_now
    assert items[0].last_modified == time_now


def test_resources_get_single(client):
    """
    Given: An existing resource in the collection
    When: When a call is made to get it by its unique keys
    Then: The resource is mapped correctly, 200 status
    """
    # Arrange

    time_now = datetime.utcnow()
    ResourceFactory(
        name="Res One",
        reference="res_1",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=time_now,
        last_seen=time_now,
    )
    ResourceFactory(
        name="Res Two",
        reference="res_2",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=time_now,
        last_seen=time_now,
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/resources/?applicationEnvironmentId=1&reference=res_2",
    )
    # Assert
    assert resp.status_code == 200

    # Assert Response
    data = resp.get_json()

    assert data["id"] == 2
    assert data["name"] == "Res Two"
    assert data["reference"] == "res_2"
    assert data["applicationEnvironmentId"] == 1
    assert data["resourceTypeId"] == 20


def test_resources_get_single_not_found(client):
    """
    Given: An existing resource in the collection
    When: When a call is made to get a resource which is not present by its unique keys
    Then: 404 status
    """
    # Arrange
    time_now = datetime.utcnow()
    ResourceFactory(
        name="Res One",
        reference="res_1",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=time_now,
        last_seen=time_now,
    )
    ResourceFactory(
        name="Res Two",
        reference="res_2",
        resource_type_id=20,
        application_environment_id=1,
        last_modified=time_now,
        last_seen=time_now,
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/resources/?applicationEnvironmentId=1&reference=res_99999",
    )
    # Assert
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "test_input",
    [
        "applicationEnvironmentId=999&reference=res_1",
        "applicationEnvironmentId=1&reference=res_blah",
        "reference=res_1",
        "applicationEnvironmentId=1",
    ],
)
def test_resources_put_throws_bad_request_when_params_do_not_match(client, test_input):
    """
    Given: No existing resource in the collection
    When: When a call is made to update a resource but the query params do not match the payload
    Then: A 400 error is returned
    """
    # Arrange

    # Act
    resp = client.put(
        f"/resources/?{test_input}",
        json={
            "name": "Res One",
            "reference": "res_1",
            "resourceTypeId": 20,
            "applicationEnvironmentId": 1,
        },
    )
    # Assert
    assert resp.status_code == 400
    assert (
        resp.get_json()["message"]
        == "Keys in data do not match the keys in the query parameters"
    )
