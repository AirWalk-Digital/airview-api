from tests.client_tests.common import *
from airview_api import app
from airview_api.database import db
from airview_api.models import (
    TechnicalControlSeverity,
    ExclusionState,
    MonitoredResourceState,
)
from datetime import datetime
from tests.common import client, instance
from tests.factories import *
import requests_mock
from requests_flask_adapter import Session
import pytest

from client.airviewclient import models


def setup():
    setup_factories()

    SystemFactory(id=111, name="one")
    EnvironmentFactory(id=1)
    ApplicationFactory(id=11, parent_id=None, name="svc 13", environment_id=1)
    ApplicationReferenceFactory(
        id=311, application_id=11, type="aws_account_id", reference="ref-1"
    )
    TechnicalControlFactory(
        id=22,
        name="ctl1",
        reference="control_a",
        control_type_id=1,
        system_id=111,
        severity=TechnicalControlSeverity.HIGH,
    )
    ApplicationTechnicalControlFactory(
        id=33, application_id=11, technical_control_id=22
    )

    ExclusionFactory(
        id=44,
        application_technical_control_id=33,
        summary="sss",
        mitigation="mmm",
        impact=3,
        probability=4,
        is_limited_exclusion=True,
        end_date=datetime(1, 1, 1),
        notes="nnn",
    )
    MonitoredResourceFactory(
        id=55,
        exclusion_id=44,
        reference="res-a",
        exclusion_state=ExclusionState.PENDING,
        state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=33,
    )

    MonitoredResourceFactory(
        id=56,
        exclusion_id=44,
        reference="res-5",
        exclusion_state=ExclusionState.PENDING,
        state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=33,
    )
    MonitoredResourceFactory(
        id=57,
        exclusion_id=44,
        reference="res-6",
        exclusion_state=ExclusionState.ACTIVE,
        state=MonitoredResourceState.FIXED_AUTO,
        last_modified=datetime(1, 1, 1),
        last_seen=datetime(2, 1, 1),
        application_technical_control_id=33,
    )


def test_get_exclusions_filters_correctly(handler):
    """
    Given: Populated exclusion resources
    When: When a call is made to list by state
    Then: The correct state is filtered in the response
    """
    # Arrange

    # Act
    pending = list(
        handler.get_exclusions_by_state(models.ExclusionResourceState.PENDING)
    )
    assert len(pending) == 2
    assert next((x for x in pending if x.id == 55), None) is not None
    assert next((x for x in pending if x.id == 56), None) is not None


def test_handle_exclusion_resource_updates_state(handler):
    """
    Given: Populated exclusion resources
    When: When a call is made to list by state
    Then: The correct state is filtered in the response
    """
    # Arrange
    exclusion_resource = models.ExclusionResource(
        id=55,
        state=models.ExclusionResourceState.ACTIVE,
        reference="a",
        technical_control_reference="b",
        application_reference="c",
    )

    # Act
    handler.set_exclusion_resource_state(
        id=55, state=models.ExclusionResourceState.ACTIVE
    )

    # Assert
    item = MonitoredResource.query.get(55)
    assert item.exclusion_state == ExclusionState.ACTIVE
    print(item)
