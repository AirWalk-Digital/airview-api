import pytest
from pprint import pprint
from airview_api.models import Application, SystemStage

from tests.common import client
from tests.factories import *


def setup():
    ApplicationFactory.reset_sequence()
    EnvironmentFactory.reset_sequence()
    SystemFactory.reset_sequence()


def test_application_get_single_ok(client):
    """
    Given: A collection of applications exist in the database
    When: When the api is called with an id
    Then: The corrisponding application is returned with status 200
    """
    # Arrange
    EnvironmentFactory(id=1)
    # ApplicationFactory.create_batch(5)
    ApplicationFactory(
        id=1, environment_id=1, application_type=ApplicationType.BUSINESS_APPLICATION
    )
    ApplicationFactory(
        id=2,
        name="myapp1",
        environment_id=1,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=3, environment_id=1, application_type=ApplicationType.BUSINESS_APPLICATION
    )
    ApplicationReferenceFactory(
        id=3, application_id=2, type="type123", reference="valabc"
    )

    # Act
    resp = client.get("/applications/2")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["id"] == 2
    assert data["name"] == "myapp1"
    assert data["applicationType"] == "BUSINESS_APPLICATION"
    assert len(data["references"]) == 1
    assert data["references"][0]["type"] == "type123"
    assert data["references"][0]["reference"] == "valabc"


def test_application_get_single_not_found(client):
    """
    Given: A collection of applications exists in the database
    When: When the id does not exit in the database
    Then: Status 404 is returned with an empty response
    """
    # Arrange
    EnvironmentFactory(id=1)
    ApplicationFactory.create_batch(5)

    # Act
    resp = client.get("/applications/10")

    # Assert
    assert resp.status_code == 404


def test_application_post_ok_response(client):
    """
    Given: An empty application collection in the db
    When: When an application definition is posted to the api
    Then: The application is returned with a new id populated, status 200 and stored in db
    """
    # Arrange
    EnvironmentFactory(id=1)
    SystemFactory(id=2, stage=SystemStage.BUILD)

    # Act
    resp = client.post(
        "/applications/",
        json={
            "name": "App 1",
            "applicationType": "BUSINESS_APPLICATION",
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
    assert data["name"] == "App 1"
    assert data["environmentId"] == data["environmentId"]
    assert len(data["references"]) == 3
    assert data["references"][1]["type"] == "type1"
    assert data["references"][1]["reference"] == "val1"

    # Assert persistance
    items = db.session.query(Application).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "App 1"
    assert items[0].environment_id == data["environmentId"]

    assert len(items[0].references.all()) == 3
    assert items[0].references.filter_by(type="type1").first().reference == "val1"


def test_application_post_handles_existing_app(client):
    """
    Given: 2 exiting application in the db
    When: When an application definition with existing name is posted to the api
    Then: The application is persisted with _1 appended to the id
    """
    # Arrange
    app_one = ApplicationFactory()
    app_two = ApplicationFactory()
    ApplicationReferenceFactory(
        application=app_one, type="_internal_reference", reference="app_1"
    )
    ApplicationReferenceFactory(
        application=app_two, type="_internal_reference", reference="app_1_0"
    )

    EnvironmentFactory(id=1)
    SystemFactory(id=2, stage=SystemStage.BUILD)
    items = db.session.query(Application).all()

    # Act
    resp = client.post(
        "/applications/",
        json={
            "name": "App 1",
            "applicationType": "BUSINESS_APPLICATION",
        },
    )

    # Assert return
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["references"]) == 1
    assert data["references"][0]["type"] == "_internal_reference"
    assert data["references"][0]["reference"] == "app_1_1"

    # Assert persistance
    items = db.session.query(Application).all()
    assert len(items) == 3
    assert len(items[2].references.all()) == 1
    assert (
        items[2].references.filter_by(type="_internal_reference").first().reference
        == "app_1_1"
    )


def test_application_post_handles_duplication_loop(client):
    """
    Given: 10 exiting application in the db with the same name
    When: When an application definition with the same existing name is posted to the api
    Then: A 400 error is returned
    """
    # Arrange
    EnvironmentFactory(id=1)
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(id=99)
    ApplicationReferenceFactory(
        application_id=99, type="_internal_reference", reference="app_1"
    )
    for i in range(0, 9):
        ApplicationFactory(id=i)
        ApplicationReferenceFactory(
            application_id=i, type="_internal_reference", reference="app_1_" + str(i)
        )

    # Act
    resp = client.post(
        "/applications/",
        json={
            "name": "App 1",
            "applicationType": "BUSINESS_APPLICATION",
        },
    )

    # Assert return
    print(resp.json)
    assert resp.status_code == 400
    assert b"Cannot generate unique name. Too many duplicates" in resp.data


def test_application_post_rejects_bad_reference_type(client):
    """
    Given: No application types exist in the database
    When: When an application definition is posted to the api with disallowed reference type(url escaped chars)
    Then: A 422 status is returned, no data persisted
    """
    # Arrange

    # Act
    resp = client.post(
        "/applications/",
        json={
            "name": "App 1",
            "applicationType": "BUSINESS_APPLICATION",
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
        "/applications/",
        json={
            "name": "App 1",
            "applicationType": "BUSINESS_APPLICATION",
            "references": [{"type": "good_key", "reference": "bad&ref"}],
        },
    )

    # Assert
    assert resp.status_code == 422
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_post_bad_request_for_unknown_app_type(client):
    """
    Given: No application types exist in the database
    When: When an application definition is posted to the api
    Then: A bad request is returned
    """
    # Arrange

    # Act
    resp = client.post(
        "/applications/",
        json={
            "name": "App 1",
            "applicationType": "UNKNOWN_APPLICATION",
        },
    )

    # Assert
    assert resp.status_code == 400


@pytest.mark.parametrize(
    "data",
    [
        {},
        {
            "xxxname": "App 1",
            "reference": "ref_1",
            "applicationType": "BUSINESS_APPLICATION",
        },
        {
            "name": "App 1",
            "xxxreference": "ref_1",
            "applicationType": "BUSINESS_APPLICATION",
        },
        {
            "name": "App 1",
            "reference": "ref_1",
            "xxxapplicationType": "BUSINESS_APPLICATION",
        },
        {"id": 123, "name": "App 1", "reference": "ref_1"},
        {
            "id": 0,
            "name": "App 1",
            "reference": "ref_1",
            "applicationType": "BUSINESS_APPLICATION",
        },
    ],
)
def test_application_post_bad_request_for_id(client, data):
    """
    Given: An empty database
    When: When an invalid application definition is sent to the api
    Then: The api returns with status 400/422 (depends on marshmallow validation) and no data is persisted to the database
    """
    # Arrange

    # Act
    resp = client.post("/applications/", json=data)

    # Assert
    assert resp.status_code in [400, 422]
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_applications_get_all(client):
    """
    Given: A collection of applications in the db
    When: When a call is made to the root resource
    Then: An array of all applications is returned in alphabetical order with status 200
    """
    # Arrange
    EnvironmentFactory(id=1)
    ApplicationFactory(id=1, name="zzz")
    ApplicationFactory(id=2, name="aaa")
    ApplicationFactory(id=3, name="bbb")
    ApplicationFactory(id=4, name="xxx")
    ApplicationFactory(id=5, name="yyy")

    # Act
    resp = client.get("/applications/")

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 5

    assert data[2]["id"] == 3
    assert data[2]["name"] == "bbb"
    assert data[2]["applicationType"] == "BUSINESS_APPLICATION"

    assert data[0]["name"] == "zzz"
    assert data[4]["name"] == "yyy"


def test_applications_get_by_application_type(client):
    """
    Given: A collection of applications in the db
    When: When a request is made for a specifc type of application
    Then: Only appications with the correct type are returned
    """
    # Arrange
    EnvironmentFactory(id=11)
    ApplicationFactory(
        id=1,
        name="App 1",
        application_type=ApplicationType.APPLICATION_SERVICE,
        environment_id=11,
    )
    ApplicationFactory(
        id=2, name="App 2", application_type=ApplicationType.TECHNICAL_SERVICE
    )
    ApplicationFactory(
        id=3,
        name="App 3",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=11,
    )
    ApplicationFactory(
        id=4, name="App 4", application_type=ApplicationType.BUSINESS_APPLICATION
    )
    ApplicationFactory(
        id=5, name="App 5", application_type=ApplicationType.APPLICATION_SERVICE
    )

    # Act
    resp = client.get("/applications/?applicationType=BUSINESS_APPLICATION")

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2

    assert data[0]["name"] == "App 3"
    assert data[0]["applicationType"] == "BUSINESS_APPLICATION"


def test_applications_post_child_application_ok(client):
    """
    Given: A collection of applications in the db
    When: When a request is made to persist a child application  with a valid parent
    Then: The application is persisted in the db
    """
    # Arrange
    EnvironmentFactory(id=1)
    app = ApplicationFactory(
        id=3, application_type=ApplicationType.BUSINESS_APPLICATION
    )

    resp = client.post(
        "/applications/",
        json={
            "name": "App Service 1",
            "applicationType": "BUSINESS_APPLICATION",
            "parentId": 3,
        },
    )

    # Assert return
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["name"] == "App Service 1"
    assert data["parentId"] == app.id

    # Assert persistance
    items = db.session.query(Application).filter_by(parent_id=3).all()
    assert len(items) == 1
    assert items[0].name == "App Service 1"
    assert items[0].parent_id == 3


def test_application_post_bad_request_for_missing_parent(client):
    """
    Given: An empty application table, populated application and environmnt tables
    When: When a contraint violation occours in the database #
    Then: The api returns with status 400 and no data is persisted to the database
    """
    # Arrange
    EnvironmentFactory(id=3)
    input_data = {
        "name": "App 1",
        "applicationType": "BUSINESS_APPLICATION",
        "parentId": 2,
        "environmentId": 3,
    }

    # Act
    resp = client.post("/applications/", json=input_data)

    # Assert
    assert resp.status_code == 400
    assert b"Integrity Error" in resp.data
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
    input_data = {
        "name": "App 1",
        "applicationType": "BUSINESS_APPLICATION",
        "parentId": 2,
        "environmentId": 3,
    }

    # Act
    resp = client.post("/applications/", json=input_data)

    # Assert
    assert resp.status_code == 400
    assert b"Integrity Error" in resp.data
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_post_bad_request_for_missing_app_type(client):
    """
    Given: An empty application table, populated application and environmnt tables
    When: When a contraint violation occours in the database
    Then: The api returns with status 400 and no data is persisted to the database
    """
    # Arrange
    ApplicationFactory(id=2)
    EnvironmentFactory(id=3)
    input_data = {
        "name": "App 1",
        "applicationType": "NONE_BUSINESS_APPLICATION",
        "parentId": 2,
        "environmentId": 3,
    }

    # Act
    resp = client.post("/applications/", json=input_data)

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
    EnvironmentFactory(id=3)
    ApplicationFactory(id=222, name="parent")
    ApplicationFactory(id=333, name="parent-333")
    ApplicationFactory(
        id=111,
        name="child",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        parent_id=222,
        environment_id=3,
    )

    # Act
    resp = client.put(
        "/applications/111",
        json={
            "id": 111,
            "name": "MyApp",
            "applicationType": "BUSINESS_APPLICATION",
            "environmentId": 1,
            "parentId": 333,
        },
    )

    # Assert return
    assert resp.status_code == 204

    # Assert persistance
    items = db.session.query(Application).all()
    item = db.session.query(Application).get(111)
    assert len(items) == 3
    assert item.id == 111
    assert item.name == "MyApp"
    assert item.environment_id == 1
    assert item.parent_id == 333


def test_application_put_handles_id_mismatch(client):
    """
    Given: An existing application in the db
    When: When an application definition is put to the api
    Then: The application is updated, 204 status
    """
    # Arrange

    # Act
    resp = client.put(
        "/applications/111",
        json={
            "id": 222,
            "name": "MyApp",
            "applicationType": "BUSINESS_APPLICATION",
            "environmentId": 1,
        },
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
        "/applications/111",
        json={
            "id": 111,
            "name": "MyApp",
            "applicationType": "BUSINESS_APPLICATION",
            "environmentId": 1,
        },
    )

    # Assert
    assert resp.status_code == 404
    items = db.session.query(Application).all()
    assert len(items) == 0


def test_application_put_handles_missing_environment(client):
    """
    Given: An existing application in the db
    When: When an application definition is put to the api with a missing environment
    Then: 204 status, environment set to null
    """
    # Arrange
    EnvironmentFactory(id=3)
    ApplicationFactory(
        id=222,
        application_type=ApplicationType.APPLICATION_SERVICE,
        environment_id=None,
        name="parent",
    )
    ApplicationFactory(
        id=111,
        name="child",
        application_type=ApplicationType.APPLICATION_SERVICE,
        environment_id=3,
    )

    # Act
    resp = client.put(
        "/applications/111",
        json={
            "id": 111,
            "name": "MyApp",
            "applicationType": "APPLICATION_SERVICE",
            "parentId": 222,
        },
    )

    # Assert return
    assert resp.status_code == 204

    item = db.session.query(Application).get(111)
    assert item.environment_id is None


def test_application_put_handles_missing_application_type(client):
    """
    Given: An existing application in the db
    When: When an application definition is put to the api with a missing type
    Then: 422 status (its a non nullable property)
    """
    # Arrange
    EnvironmentFactory(id=3)
    ApplicationFactory(id=222, name="parent")
    ApplicationFactory(
        id=111,
        name="child",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=3,
    )

    # Act
    resp = client.put(
        "/applications/111",
        json={
            "id": 111,
            "name": "MyApp",
            "parentId": 222,
            "environmentId": 3,
        },
    )

    # Assert return
    assert resp.status_code == 422


def test_application_put_handles_missing_parent(client):
    """
    Given: An existing application in the db
    When: When an application definition is put to the api with a missing parent
    Then: Parent is overwritten as null
    """
    # Arrange
    EnvironmentFactory(id=3)
    ApplicationFactory(
        id=111,
        name="child",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=3,
    )

    # Act
    resp = client.put(
        "/applications/111",
        json={
            "id": 111,
            "name": "MyApp",
            "applicationType": "BUSINESS_APPLICATION",
            "environmentId": 3,
        },
    )

    # Assert return
    assert resp.status_code == 204

    item = db.session.query(Application).get(111)
    assert item.parent_id is None
