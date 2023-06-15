from datetime import datetime, timedelta, timezone
from tests.factories import *
from tests.common import client
from airview_api.models import (
    MonitoredResource,
    MonitoredResourceState,
    SystemStage,
    TechnicalControlAction,
)
import pytest


def setup():
    reset_factories()
    EnvironmentFactory(id=1)
    SystemFactory(id=2, stage=SystemStage.BUILD)
    ApplicationFactory(
        id=1, name="App Other", application_type=ApplicationType.APPLICATION_SERVICE
    )
    ApplicationEnvironmentFactory(id=1, application_id=1, environment_id=1)
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")

    TechnicalControlFactory(
        id=1,
        reference="1",
        name="one",
        system_id=2,
    )
    ResourceFactory(
        id=11,
        name="Res One",
        reference="res_1",
        service_id=10,
        application_environment_id=1,
    )
    ResourceFactory(
        id=12,
        name="Res Two",
        reference="res_2",
        service_id=10,
        application_environment_id=1,
    )
    ResourceFactory(
        id=13,
        name="Res Deleted",
        reference="res_3",
        service_id=10,
        application_environment_id=1,
    )

    time_now = datetime.utcnow()
    MonitoredResourceFactory(
        id=301,
        resource_id=11,
        technical_control_id=1,
        monitoring_state=MonitoredResourceState.FLAGGED,
        last_modified=time_now,
        last_seen=time_now - timedelta(days=1),
        additional_data="Old",
    )

    MonitoredResourceFactory(
        id=302,
        resource_id=12,
        technical_control_id=1,
        monitoring_state=MonitoredResourceState.MONITORING,
        last_modified=time_now,
        last_seen=time_now - timedelta(days=1),
        additional_data="Old",
    )

    MonitoredResourceFactory(
        id=303,
        resource_id=13,
        technical_control_id=1,
        monitoring_state=MonitoredResourceState.DELETED,
        last_modified=time_now,
        last_seen=time_now - timedelta(days=1),
        additional_data="Old",
    )


def test_get_complaince_bad_request_for_missing_select(client):
    """
    Given: A populated set of compliance events
    When: When the compliance api is called without a $select
    Then: 400 status and error message
    """
    # Arrange
    # Act

    resp = client.get(
        "/compliance/",
    )
    assert resp.status_code == 400

    data = resp.get_json()
    assert data.get("message", "").startswith(
        "The $select query parameter must be passed"
    )


@pytest.mark.parametrize(
    "test_input", ["applicationName,nonsense", "a", "applicationNameeee", "nonsense"]
)
def test_get_complaince_bad_request_for_unknown_select(client, test_input):
    """
    Given: A populated set of compliance events
    When: When the compliance api is called with a select containing an unknown column
    Then: 400 status and error message
    """
    # Arrange
    # Act

    resp = client.get(
        f"/compliance/?$select={test_input}",
    )
    assert resp.status_code == 400

    data = resp.get_json()
    assert data.get("message", "").startswith(
        "The selection contains fields which should not be allowed. Allowed fields are:"
    )


def test_get_complaince_bad_request_for_unparsable_filter(client):
    """
    Given: A populated set of compliance events
    When: When the compliance api is called with an odata filter which cannot be pased
    Then: 400 status and error message
    """
    # Arrange
    # Act

    resp = client.get(
        "/compliance/?$select=applicationName&$filter=tt aa st ff",
    )
    assert resp.status_code == 400

    data = resp.get_json()
    assert data.get("message", "").startswith("The filter provided could not be parsed")


def test_get_complaince_bad_request_for_unexecutable_filter(client):
    """
    Given: A populated set of compliance events
    When: When the compliance api is called with an odata filter which is invalid
    Then: 400 status and error message
    """
    # Arrange
    # Act

    resp = client.get(
        "/compliance/?$select=applicationName&$filter=rubbish",
    )
    assert resp.status_code == 400

    data = resp.get_json()
    assert data.get("message", "").startswith(
        "The query could not be executed. Check the filter which was passed is valid"
    )


@pytest.mark.parametrize(
    "test_input",
    [
        {
            "query": "$select=applicationName",
            "expected": [
                {"applicationName": "App Other", "isCompliant": 1, "total": 2}
            ],
        },
        {
            "query": "$select=resourceReference",
            "expected": [
                {"isCompliant": 1, "resourceReference": "res_2", "total": 1},
                {"isCompliant": 0, "resourceReference": "res_1", "total": 1},
            ],
        },
        {
            "query": "$select=resourceReference&$filter=resourceReference eq 'res_2'",
            "expected": [
                {"isCompliant": 1, "resourceReference": "res_2", "total": 1},
            ],
        },
    ],
)
def test_get_complaince_ok_for_valid_query_with_missing_filter(client, test_input):
    """
    Given: A populated set of compliance events
    When: When the compliance api is called with a missing filter
    Then: 200 status and the correct aggregation is returned
    """
    # Arrange
    # Act

    resp = client.get(
        f"/compliance/?{test_input['query']}",
    )
    assert resp.status_code == 200

    data = resp.get_json()

    assert data == test_input["expected"]
