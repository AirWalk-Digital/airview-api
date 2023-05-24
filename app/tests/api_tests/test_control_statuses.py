from datetime import datetime
from tests.common import client
from tests.factories import *
from airview_api.models import (
    Application,
    ApplicationTechnicalControl,
    MonitoredResource,
    MonitoredResourceState,
    TechnicalControlSeverity,
    SystemStage,
)


def test_control_status_detail_returns_correct_detail(client):
    """
    Given: An exitsting monitored resource
    When: When a correctly formed request to get the detail is sent
    Then: The detail is returned, 200 status
    """
    # Arrange
    SystemFactory(id=1, name="one", stage=SystemStage.BUILD)
    EnvironmentFactory(id=1, name="aaa")
    ApplicationFactory(id=1, application_type=ApplicationType.BUSINESS_APPLICATION)
    ApplicationFactory(id=12, parent_id=1, environment_id=1, name="App Svc 2")
    TechnicalControlFactory(
        id=22,
        name="ctrl three",
        reference="three",
        system_id=1,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=33, application_id=12, technical_control_id=22
    )
    ResourceFactory(
        id=999,
        reference="ref-1",
        type=MonitoredResourceType.DATABASE,
        last_seen=datetime.utcnow(),
        last_modified=datetime.utcnow(),
    )
    MonitoredResourceFactory(
        id=111,
        resource_id=999,
        application_technical_control_id=33,
        monitoring_state=MonitoredResourceState.SUPPRESSED,
        last_seen=datetime.utcnow(),
        last_modified=datetime.utcnow(),
    )
    url = "/control-statuses/111/control-status-detail"
    # Act
    resp = client.get(url)
    data = resp.get_json()

    # Assert
    assert resp.status_code == 200

    assert data["id"] == 111
    assert data["applicationName"] == "App Svc 2"
    assert data["control"]["name"] == "ctrl three"
    assert data["control"]["url"] == None
    assert data["frameworks"] == []
    assert data["assignmentGroup"] == None
    assert data["assignmentGroup"] == None
