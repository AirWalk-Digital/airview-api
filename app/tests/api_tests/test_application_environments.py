import pytest
from pprint import pprint
from airview_api.models import Application, SystemStage

from tests.common import client
from tests.factories import *


def setup():
    reset_factories()


def test_application_environment_get_single_ok(client):
    """
    Given: A collection of application environments exist in the database
    When: When the api is called with an id
    Then: The corrisponding application is returned with status 200
    """
    # Arrange
    EnvironmentFactory(id=1)
    EnvironmentFactory(id=2)
    # ApplicationFactory.create_batch(5)
    ApplicationFactory(id=10, application_type=ApplicationType.BUSINESS_APPLICATION)
    ApplicationEnvironmentFactory(id=20, application_id=10, environment_id=1)
    ApplicationEnvironmentFactory(id=21, application_id=10, environment_id=2)

    ApplicationEnvironmentReferenceFactory(
        id=30, application_environment_id=20, type="ref", reference="ref-1"
    )
    ApplicationEnvironmentReferenceFactory(
        id=31, application_environment_id=20, type="different-ref", reference="ref-2"
    )
    ApplicationEnvironmentReferenceFactory(
        id=32, application_environment_id=21, type="ref", reference="ref-other"
    )

    # Act
    resp = client.get("/application-environments/20")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["id"] == 20
    assert data["environmentId"] == 1
    assert data["application"] == {
        "applicationType": "BUSINESS_APPLICATION",
        "id": 10,
        "name": "App 0",
    }
    assert data["references"] == [
        {"reference": "ref-2", "type": "different-ref"},
        {"reference": "ref-1", "type": "ref"},
    ]


def test_application_environment_get_single_not_found(client):
    """
    Given: A collection of application environments exists in the database
    When: When the id does not exit in the database
    Then: Status 404 is returned with an empty response
    """
    # Arrange
    EnvironmentFactory(id=1)
    ApplicationEnvironmentFactory.create_batch(5)

    # Act
    resp = client.get("/applications-environments/10")

    # Assert
    assert resp.status_code == 404


def test_application_envionment_post_ok_response(client):
    """
    Given: An empty application collection in the db
    When: When an application definition is posted to the api
    Then: The application is returned with a new id populated, status 200 and stored in db
    """
    # Arrange
    EnvironmentFactory(id=1)
    ApplicationFactory(id=11, name="TestApp")

    # Act
    resp = client.post(
        "/application-environments/",
        json={
            "applicationId": 11,
            "environmentId": 1,
            "references": [
                {"type": "type1", "reference": "val1"},
                {"type": "type2", "reference": "val2"},
            ],
        },
    )

    # Assert return
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 1
    assert data["environmentId"] == data["environmentId"]
    assert data["applicationId"] == data["applicationId"]
    assert len(data["references"]) == 2
    assert data["references"][1]["type"] == "type2"
    assert data["references"][1]["reference"] == "val2"

    # Assert persistance
    items = db.session.query(ApplicationEnvironment).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].environment_id == data["environmentId"]
    assert items[0].application_id == data["applicationId"]

    assert items[0].references.count() == 2
    assert items[0].references.filter_by(type="type1").first().reference == "val1"


def test_application_post_rejects_bad_reference_type(client):
    """
    Given: No application types exist in the database
    When: When an application definition is posted to the api with disallowed reference type(url escaped chars)
    Then: A 422 status is returned, no data persisted
    """
    # Arrange

    # Act
    resp = client.post(
        "/application-environments/",
        json={
            "applicationId": 11,
            "environmentId": 1,
            "references": [{"type": "bad key", "reference": "good_ref"}],
        },
    )

    # Assert
    assert resp.status_code == 422
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_post_rejects_bad_reference_value(client):
    """
    Given: No application types exist in the database
    When: When an application definition is posted to the api with disallowed reference value(url escaped chars)
    Then: A 422 status is returned, no data persisted
    """
    # Arrange

    # Act
    resp = client.post(
        "/application-environments/",
        json={
            "applicationId": 11,
            "environmentId": 1,
            "references": [{"type": "good_key", "reference": "bad&ref"}],
        },
    )

    # Assert
    assert resp.status_code == 422
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_post_bad_request_for_missing_environment(client):
    """
    Given: An empty application table, populated application and environmnt tables
    When: When a contraint violation occours in the database
    Then: The api returns with status 400 and no data is persisted to the database
    """
    # Arrange
    ApplicationFactory(id=2)
    input_data = {"applicationId": 2, "environmentId": 3, "references": []}

    # Act
    resp = client.post("/application-environments/", json=input_data)

    # Assert
    assert resp.status_code == 400
    assert b"Integrity Error" in resp.data
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_put_ok(client):
    """
    Given: An existing application in the db
    When: When an application definition is put to the api
    Then: The application is updated, 204 status
    """
    # Arrange
    EnvironmentFactory(id=1)
    EnvironmentFactory(id=2)
    ApplicationFactory(
        id=10,
        name="One",
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=12,
        name="Two",
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationEnvironmentFactory(id=20, application_id=10, environment_id=1)
    ApplicationEnvironmentReferenceFactory(
        id=31, application_environment_id=20, type="different-ref", reference="ref-2"
    )

    # Act
    resp = client.put(
        "/application-environments/20",
        json={
            "id": 20,
            "environmentId": 2,
            "applicationId": 12,
            "references": [
                {"type": "new-ref", "reference": "new-1"},
                {"type": "new-ref-other", "reference": "new-2"},
            ],
        },
    )

    # Assert return
    assert resp.status_code == 204

    # Assert persistance
    items = db.session.query(ApplicationEnvironment).all()
    assert len(items) == 1
    assert items[0].id == 20
    assert items[0].environment_id == 2
    assert items[0].application_id == 12

    references = db.session.query(ApplicationEnvironmentReference).all()
    assert len(references) == 2
    assert references[0].type == "new-ref"
    assert references[0].reference == "new-1"
    assert references[1].type == "new-ref-other"
    assert references[1].reference == "new-2"


def test_application_put_handles_id_mismatch(client):
    """
    Given: An existing application in the db
    When: When an application definition is put to the api
    Then: The application is updated, 204 status
    """
    # Arrange

    # Act
    resp = client.put(
        "/application-environments/111",
        json={"id": 222, "applicationId": 2, "environmentId": 1, "references": []},
    )

    # Assert
    assert resp.status_code == 400
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_put_handles_not_found(client):
    """
    Given: An empty db
    When: When an application definition is put to the api
    Then: 404 is returned, no data change
    """
    # Arrange

    # Act
    resp = client.put(
        "/application-environments/111",
        json={"id": 111, "environmentId": 1, "applicationId": 1, "references": []},
    )

    # Assert
    assert resp.status_code == 404
    items = db.session.query(ApplicationEnvironment).all()
    assert len(items) == 0
