from datetime import datetime, timedelta
from airview_api.models import Framework, FrameworkControlObjective, FrameworkControlObjectiveLink, FrameworkSection
from tests.common import client
from tests.factories import *
import pytest


def setup():
    reset_factories()


def test_frameworks_post_ok(client):
    """
    Given: Multiple frameworks exist
    When: When a call is made to persist a framework
    Then: The item is persisted and the id populated
    """
    # Arrange

    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/frameworks/",
        json={
            "name": "HIPAATEST",
            "link": "/hipaatest",
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    print(data)
    assert data["name"] == "HIPAATEST"
    assert data["link"] == "/hipaatest"

    # Assert persistance
    items = db.session.query(Framework).all()
    assert len(items) == 3
    assert items[2].id == 3
    assert items[2].name ==  "HIPAATEST"
    assert items[2].link == "/hipaatest"



def test_frameworks_get_ok(client):
    """
    Given: Frameowrks exist in the collection
    When: When a call is made to get all resources
    Then: 200 status and all resources are returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1


def test_frameworks_get_by_name(client):
    """
    Given: Frameworks exist in the collection
    When: When a call is made to get a specific resource
    Then: 200 status and the specific resource is returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/?name=NISTTEST",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == "NISTTEST"


def test_frameworks_get_missing_by_name(client):
    """
    Given: Frameworks exist in the collection
    When: When a call is made to get a specific resource that does not exist
    Then: 200 status and an empty array is returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/?name=FEDRAMP",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0


def test_framework_sections_post_ok(client):
    """
    Given: A framework exists
    When: When a call is made to add a framework section
    Then: The item is persisted and the id populated
    """
    # Arrange

    FrameworkFactory( 
        name="NISTTEST",
        link="/nisttest"
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/frameworks/1/sections",
        json={
            "name": "Access Control",
            "link": "/nisttest/access_control",
            "frameworkId": 1
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    print(data)
    assert data["name"] == "Access Control"
    assert data["link"] == "/nisttest/access_control"

    # Assert persistance
    items = db.session.query(FrameworkSection).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "Access Control"
    assert items[0].link == "/nisttest/access_control"


def test_framework_sections_get_ok(client):
    """
    Given: Frameowrks and Sections exist in the collection
    When: When a call is made to get all sections for a framework
    Then: 200 status and all the framework sections are returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    FrameworkSectionFactory(
        name="Logging",
        link="/nisttest/logging",
        framework_id=1
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    FrameworkSectionFactory(
        name="Identity",
        link="/ccmtest/identity",
        framework_id=2
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/1/sections",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2


def test_framework_sections_get_by_name(client):
    """
    Given: Frameowrks and Sections exist in the collection
    When: When a call is made to get a specific section
    Then: 200 status and the specific resource is returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    FrameworkSectionFactory(
        name="Logging",
        link="/nisttest/logging",
        framework_id=1
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    FrameworkSectionFactory(
        name="Identity",
        link="/ccmtest/identity",
        framework_id=2
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/1/sections?name=Logging",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == "Logging"


def test_framework_sections_get_missing_by_name(client):
    """
    Given: Frameowrks and Sections exist in the collection
    When: When a call is made to get a specific resource that does not exist
    Then: 200 status and an empty array is returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    FrameworkSectionFactory(
        name="Logging",
        link="/nisttest/logging",
        framework_id=1
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    FrameworkSectionFactory(
        name="Identity",
        link="/ccmtest/identity",
        framework_id=2
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/1/sections?name=Monitoring",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0


def test_framework_control_objective_post_ok(client):
    """
    Given: A framework and sections exist
    When: When a call is made to add a control to a section
    Then: The item is persisted and the id populated
    """
    # Arrange

    FrameworkFactory( 
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    db.session.commit()

    # Act
    resp = client.post(
        "/frameworks/1/sections/1/control_objectives",
        json={
            "name": "Ensure 2FA is enabled",
            "link": "/nisttest/access_control/ensure_2fa_is_enabled",
            "frameworkSectionId": 1
        },
    )
    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    print(data)
    assert data["name"] == "Ensure 2FA is enabled"
    assert data["link"] == "/nisttest/access_control/ensure_2fa_is_enabled"

    # Assert persistance
    items = db.session.query(FrameworkControlObjective).all()
    assert len(items) == 1
    assert items[0].id == 1
    assert items[0].name == "Ensure 2FA is enabled"
    assert items[0].link == "/nisttest/access_control/ensure_2fa_is_enabled"



def test_framework_control_objective_get_ok(client):
    """
    Given: Frameowrks exist in the collection
    When: When a call is made to get aall resources
    Then: 200 status and all resources are returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    FrameworkSectionFactory(
        name="Logging",
        link="/nisttest/logging",
        framework_id=1
    )

    FrameworkControlObjectiveFactory(
        name="Ensure activity logs are sent to SIEM",
        link="/nisttest/logging/ensure_activity_logs_are_sent_to_siem",
        framework_section_id=2
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    FrameworkSectionFactory(
        name="Identity",
        link="/ccmtest/identity",
        framework_id=2
    )

    FrameworkControlObjectiveFactory(
        name="Ensure activity logs are sent to SIEM",
        link="/ccmtest/identity/ensure_activity_logs_are_sent_to_siem",
        framework_section_id=3
    )
    FrameworkControlObjectiveFactory(
        name="Users password must be at least 20 characters long",
        link="/ccmtest/identity/users_password_must_be_at_least_20_characters_long",
        framework_section_id=3
    )
    FrameworkControlObjectiveFactory(
        name="Inactive accounts should be deleted after 90 days",
        link="/ccmtest/identity/inactive_accounts_should_be_deleted_after_90_days",
        framework_section_id=3
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/2/sections/3/control_objectives",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 3


def test_framework_control_objective_get_by_name(client):
    """
    Given: Frameworks exist in the collection
    When: When a call is made to get a specific resource
    Then: 200 status and the specific resource is returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    FrameworkSectionFactory(
        name="Logging",
        link="/nisttest/logging",
        framework_id=1
    )

    FrameworkControlObjectiveFactory(
        name="Ensure activity logs are sent to SIEM",
        link="/nisttest/logging/ensure_activity_logs_are_sent_to_siem",
        framework_section_id=1
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    FrameworkSectionFactory(
        name="Identity",
        link="/ccmtest/identity",
        framework_id=2
    )

    FrameworkControlObjectiveFactory(
        name="Ensure activity logs are sent to SIEM",
        link="/ccmtest/identity/ensure_activity_logs_are_sent_to_siem",
        framework_section_id=3
    )
    FrameworkControlObjectiveFactory(
        name="Users password must be at least 20 characters long",
        link="/ccmtest/identity/users_password_must_be_at_least_20_characters_long",
        framework_section_id=3
    )
    FrameworkControlObjectiveFactory(
        name="Inactive accounts should be deleted after 90 days",
        link="/ccmtest/identity/inactive_accounts_should_be_deleted_after_90_days",
        framework_section_id=3
    )

    db.session.commit()

    # Act
    resp = client.get(
        "/frameworks/2/sections/1/control_objectives?name=Users password must be at least 20 characters long",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == "Users password must be at least 20 characters long"
    assert data[0]['id'] == 3


def test_framework_control_objective_get_missing_by_name(client):
    """
    Given: Frameworks exist in the collection
    When: When a call is made to get a specific resource that does not exist
    Then: 200 status and an empty array is returned
    """
    # Arrange
    FrameworkFactory(
        name="NISTTEST",
        link="/nisttest"
    )

    FrameworkSectionFactory(
        name="Access Control",
        link="/nisttest/access_control",
        framework_id=1
    )

    FrameworkSectionFactory(
        name="Logging",
        link="/nisttest/logging",
        framework_id=1
    )

    FrameworkControlObjectiveFactory(
        name="Ensure activity logs are sent to SIEM",
        link="/nisttest/logging/ensure_activity_logs_are_sent_to_siem"
    )

    FrameworkFactory(
        name="CCMTEST",
        link="/ccmtest"
    )

    FrameworkSectionFactory(
        name="Identity",
        link="/ccmtest/identity",
        framework_id=2
    )

    FrameworkControlObjectiveFactory(
        name="Ensure activity logs are sent to SIEM",
        link="/ccmtest/identity/ensure_activity_logs_are_sent_to_siem",
        framework_section_id=3
    )

    FrameworkControlObjectiveFactory(
        name="Inactive accounts should be deleted after 90 days",
        link="/ccmtest/identity/inactive_accounts_should_be_deleted_after_90_days",
        framework_section_id=3
    )

    db.session.commit()

    # Act
    resp = client.get(
         "/frameworks/2/sections/1/control_objectives?name=Users password must be at least 20 characters long",
    )
    data = resp.get_json()
    # Assert
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0
