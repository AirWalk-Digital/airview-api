from os import environ
from pprint import pprint
import pytest
from tests.factories import *
from tests.common import client


def setup():
    ApplicationFactory.reset_sequence()
    EnvironmentFactory.reset_sequence()


def test_get_environments_by_app_service_empty_array_for_not_found_app(client):
    """
    Given: A collection of applications exist in the database
    When: When a call is made to list the evironnments with an application id which does not exist
    Then: A unique list of environments for application services is returned with status 200
    """
    # Arrange

    # Act
    resp = client.get("/applications/2/environments")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert data == []


def test_get_environments_by_app_service_ok(client):
    """
    Given: A collection of application services exist in the database
    When: When the api is called with an application id
    Then: A unique list of environments for application services is returned with status 200
    """
    # Arrange
    ApplicationFactory(
        id=1, name="App 1", application_type=ApplicationType.BUSINESS_APPLICATION
    )
    ApplicationFactory(
        id=2, name="App 2", application_type=ApplicationType.BUSINESS_APPLICATION
    )
    EnvironmentFactory(id=11, name="Development", abbreviation="DEV")
    EnvironmentFactory(id=12, name="Production", abbreviation="PRD")
    EnvironmentFactory(id=13, name="User Acceptance", abbreviation="UAT")

    ApplicationFactory(
        id=21,
        parent_id=1,
        environment_id=11,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=22,
        parent_id=1,
        environment_id=12,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=23,
        parent_id=1,
        environment_id=13,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )

    ApplicationFactory(
        id=24,
        parent_id=2,
        environment_id=11,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=25,
        parent_id=2,
        environment_id=11,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=26,
        parent_id=2,
        environment_id=13,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )

    # Act
    resp = client.get("/applications/2/environments")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 2

    expected1 = {"abbreviation": "UAT", "id": 13, "name": "User Acceptance"}
    expected2 = {"abbreviation": "DEV", "id": 11, "name": "Development"}

    data[0] == expected1 or data[0] == expected2
    data[1] == expected1 or data[1] == expected2
    data[0] != data[1]


def test_get_environments_by_app_service_handles_none_environment(client):
    """
    Given: A collection of application services exist in the database
    When: When the api is called with an application id
    Then: A unique list of environments for application services is returned with status 200
    """
    # Arrange
    EnvironmentFactory(id=11, name="Development", abbreviation="DEV")
    EnvironmentFactory(id=12, name="Production", abbreviation="PRD")
    EnvironmentFactory(id=13, name="User Acceptance", abbreviation="UAT")
    ApplicationFactory(
        id=1,
        name="App 1",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=12,
    )
    ApplicationFactory(
        id=2, name="App 2", application_type=ApplicationType.BUSINESS_APPLICATION
    )

    ApplicationFactory(
        id=21,
        parent_id=1,
        environment_id=11,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=22,
        parent_id=1,
        environment_id=12,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=23,
        parent_id=1,
        environment_id=13,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )

    ApplicationFactory(
        id=24,
        parent_id=2,
        environment_id=11,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=25,
        parent_id=2,
        environment_id=11,
        application_type=ApplicationType.BUSINESS_APPLICATION,
    )
    ApplicationFactory(
        id=26, parent_id=2, application_type=ApplicationType.BUSINESS_APPLICATION
    )

    # Act
    resp = client.get("/applications/2/environments")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 2

    expected1 = {"abbreviation": "UAT", "id": 12, "name": "User Acceptance"}
    expected2 = {"abbreviation": "DEV", "id": 11, "name": "Development"}

    data[0] == expected1 or data[0] == expected2
    data[1] == expected1 or data[1] == expected2
    data[0] != data[1]


def test_enviromments_get_all_ok(client):
    """
    Given: A set of environments exist in the database
    When: When a call is made to the root resource
    Then: An array of application types is returned with status 200
    """
    # Arrange
    EnvironmentFactory.create_batch(5)

    # Act
    resp = client.get("/environments/")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 5

    assert data[3]["id"] == 3
    assert data[3]["name"] == "Env 3"
    assert data[3]["abbreviation"] == "E3"


def test_environment_post_ok_response(client):
    """
    Given: An empty environment collection in the db
    When: When an environment definition is posted to the api
    Then: The environment is returned with a new id populated, status 200 and stored in db
    """
    # Arrange

    # Act
    resp = client.post(
        "/environments/",
        json={"name": "Production", "abbreviation": "PRD"},
    )

    # Assert return
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 1
    assert data["name"] == "Production"
    assert data["abbreviation"] == "PRD"

    # Assert persistance
    items = db.session.query(Environment).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "Production"
    assert items[0].abbreviation == "PRD"


def test_environment_post_prevents_duplicate_abbreviations(client):
    """
    Given: A set of envrionmment in the db
    When: When an environment definition is posted to the api with a repeated abbreviation
    Then: The environment is rejected with a 400 status code
    """
    # Arrange
    EnvironmentFactory(name="Test aaa", abbreviation="AAA")
    db.session.commit()

    # Act
    resp = client.post(
        "/environments/",
        json={"name": "Other aaa", "abbreviation": "AAA"},
    )
    # Assert
    assert resp.status_code == 400
    items = db.session.query(Environment).all()
    assert len(items) == 1


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"xxxname": "Env a", "abbreviation": "XXX"},
        {"name": "Env a", "xxabbreviation": "XXX"},
        {"id": 1, "xxxname": "Env a", "abbreviation": "XXX"},
    ],
)
def test_environment_post_4xx_for_bad_data(client, data):
    """
    Given: An empty database
    When: When an invalid environment definition is sent to the api
    Then: The api returns with status 400/422 (marshmallow validation) and no data is persisted to the database
    """
    # Arrange

    # Act
    resp = client.post("/environments/", json=data)

    # Assert
    assert resp.status_code in (400, 422)
    items = db.session.query(Environment).all()
    assert len(items) == 0
