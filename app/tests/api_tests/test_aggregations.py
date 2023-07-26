from airview_api.database import db
from airview_api.models import (
    TechnicalControl,
    System,
    Application,
    ApplicationType,
    Environment,
    MonitoredResource,
    Exclusion,
    ControlSeverity,
)
from datetime import datetime
from tests.factories import *
from tests.common import client


def test_get_application_compliance_aggregation(client):
    """
    Given: An application ID
    When: The get_compliance_aggregation method is called
    Then: The expected aggregation data is returned
    """
    application_id = 1

    # Create test data using factories
    application = ApplicationFactory(id=application_id)
    environment = EnvironmentFactory(id=1)
    ApplicationEnvironmentFactory(id=1, application_id=application_id, environment_id=1)
    system = SystemFactory(id=1, name="Test System", stage="BUILD")
    control = ControlFactory(
        id=21,
        name="Ctrl 1",
        quality_model=QualityModel.COST_OPTIMISATION,
        severity=ControlSeverity.HIGH,
    )
    technical_control = TechnicalControlFactory(
        id=1,
        control_id=control.id,
        name="Test Control",
        reference="1",
        system_id=system.id,
        control_action=TechnicalControlAction.INCIDENT,
    )

    service = ServiceFactory(
        id=10, name="Service One", reference="ref_1", type="NETWORK"
    )

    resource_type = ResourceTypeFactory(
        id=10, name="res type one", reference="res-type-1", service_id=10
    )

    resource = ResourceFactory(
        id=1,
        name="Res BBB",
        reference="ref_1",
        resource_type_id=resource_type.id,
        application_environment_id=1,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )
    monitored_resource = MonitoredResourceFactory(
        id=1,
        resource_id=resource.id,
        last_modified=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        monitoring_state="FLAGGED",
        technical_control_id=technical_control.id,
    )
    db.session.commit()

    # Create expected result
    expected_result = [
        {
            "id": technical_control.id,
            "environmentName": environment.name,
            "systemName": system.name,
            "systemStage": system.stage.name,
            "technicalControlName": technical_control.name,
            "severity": "high",
            "controlName": control.name,
            "controlId": control.id,
            "resources": [{"id": resource.id, "name": resource.name, "status": "none"}],
            "raisedDateTime": monitored_resource.last_modified.isoformat(),
            "tickets": [],
        }
    ]

    # Make the request
    response = client.get(f"/aggregations/compliance/{application_id}")

    # Assert the response
    assert response.status_code == 200
    assert response.json == expected_result
