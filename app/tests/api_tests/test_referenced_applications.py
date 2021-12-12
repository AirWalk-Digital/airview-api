import pytest
from pprint import pprint
from airview_api.models import Application

from tests.common import client
from tests.factories import *


def setup():
    ApplicationFactory.reset_sequence()
    EnvironmentFactory.reset_sequence()
    SystemFactory.reset_sequence()


def setup_app_refs():
    EnvironmentFactory(id=1)
    ApplicationFactory(
        id=1,
        name="app one",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=1,
    )
    ApplicationReferenceFactory(application_id=1, type="account", reference="ref-1")
    ApplicationReferenceFactory(
        application_id=1, type="other-account", reference="ref-1"
    )

    ApplicationFactory(
        id=2,
        name="app two",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=1,
    )
    ApplicationReferenceFactory(application_id=2, type="account", reference="ref-2")
    ApplicationFactory(
        id=3,
        name="app three",
        application_type=ApplicationType.BUSINESS_APPLICATION,
        environment_id=1,
    )
    ApplicationReferenceFactory(application_id=3, type="account", reference="ref-3")


def test_applications_get_by_reference(client):
    """
    Given: An existing applications in the db
    When: When a request to filter by references(type/references) is made
    Then: The non matching applications are filtered from the response
    """
    # Arrange
    setup_app_refs()
    # Act
    resp = client.get("/referenced-applications/?type=account&reference=ref-1")

    # Assert
    assert resp.status_code == 200


def test_applications_get_by_reference_not_found(client):
    """
    Given: An existing applications in the db
    When: When a request to filter by references(type/references) is made with unmatched
    Then: 404 status
    """
    # Arrange
    setup_app_refs()
    # Act
    resp = client.get("/referenced-applications/?type=account&reference=ref-missing")

    # Assert
    assert resp.status_code == 404
