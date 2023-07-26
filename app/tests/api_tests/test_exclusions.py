import pytest
from pprint import pprint
from airview_api.models import (
    Application,
    SystemStage,
    QualityModel,
    ControlSeverity,
    Exclusion,
)
from tests.common import client
from tests.factories import *
from datetime import datetime


def setup():
    reset_factories()


def test_post_exclusion(client):
    """
    Given: A collection of resources in the database
    When: When the api is called with an exclusion for a resource
    Then: The exlcusion for the resource is perstisted and a 201 status returned
    """
    EnvironmentFactory(id=1)
    ApplicationFactory(
        id=1, name="App One", application_type=ApplicationType.APPLICATION_SERVICE
    )
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=1)

    ServiceFactory(
        id=10,
        name="Service One",
        reference="ref_1",
        type="NETWORK",
    )

    ResourceTypeFactory(
        id=10, name="res type one", reference="res-type-1", service_id=10
    )

    ControlFactory(
        id=21,
        name="Ctrl 1",
        quality_model=QualityModel.COST_OPTIMISATION,
        severity=ControlSeverity.HIGH,
    )

    ResourceFactory(
        id=31,
        name="Res AAA",
        reference="app_one",
        resource_type_id=10,
        application_environment_id=1,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/exclusions/",
        json={
            "summary": "Test Exclusion",
            "isLimitedExclusion": False,
            "controlId": 21,
            "resources": [31],
            "notes": "Note One",
        },
    )
    # Assert
    assert resp.status_code == 201

    exclusions = db.session.query(Exclusion).all()

    assert len(exclusions) == 1

    assert exclusions[0].summary == "Test Exclusion"
    assert exclusions[0].control_id == 21
    assert exclusions[0].is_limited_exclusion == False
    assert exclusions[0].notes == "Note One"
    assert exclusions[0].end_date == datetime.max

    assert len(exclusions[0].resources) == 1
    assert exclusions[0].resources[0].id == 31
