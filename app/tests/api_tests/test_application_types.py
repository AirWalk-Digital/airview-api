from tests.common import client
from tests.factories import *


def test_application_types_get_all_ok(client):
    """
    Given: A set of application types exist in the database
    When: When a call is made to the root resource
    Then: An array of application types is returned with status 200
    """
    # Arrange
    ApplicationTypeFactory.reset_sequence()
    ApplicationTypeFactory.create_batch(5)

    # Act
    resp = client.get("/application-types/")

    # Assert
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 5

    assert data[3]["id"] == 3
    assert data[3]["name"] == "AppType 3"
