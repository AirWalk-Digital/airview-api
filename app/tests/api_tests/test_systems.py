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
    ApplicationTypeFactory.reset_sequence()

    # Act
    resp = client.post("/systems/",
        json={
            "name": "System One",
            "source": "src",
            "stage":"stg"
            })

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "System One"
    assert data["source"] == "src"
    assert data["stage"] == "stg"
    assert data["id"] == 1

    # Assert persistance
    items = db.session.query(System).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "System One"
    assert items[0].source == "src"
    assert items[0].stage == "stg"
 
