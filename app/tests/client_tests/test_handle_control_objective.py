from tests.client_tests.common import *
from airview_api import app
from airview_api.database import db
from airview_api import models as api_models
from tests.common import client, instance
from tests.factories import *
import requests_mock
from requests_flask_adapter import Session
import pytest

from client.airviewclient import models


def setup():
    setup_factories()


def test_control_objective_creates_missing_elements(handler):
    """
    Given: A control objective
    When: When a call is made to handle the objective
    Then: The framework for that objective is created
    """
    # Arrange
    framework_name = "NISTrev5"
    framework_link = "/nistrev5"
    framework_section_name = "Maintenance"
    framework_section_link = "/nistrev5/maintenance"
    framework_control_objective_name = "MA2.1"
    framework_control_objective_link = "/nistrev5/maintenance/ma2-1"
    
    framework = models.Framework(
        name=framework_name,
        link=framework_link
    )
    framework_section = models.FrameworkSection(
        name=framework_section_name,
        link=framework_section_link,
        framework=framework
    )
    framework_control_objective = models.FrameworkControlObjective(
        name=framework_control_objective_name,
        link=framework_control_objective_link,
        framework_section=framework_section
    )

    handler.handle_framework_control_objective(framework_control_objective)

    # Assert
    framework_data = Framework.query.all()
    framewok_section_data = FrameworkSection.query.all()
    framework_control_objective_data = FrameworkControlObjective.query.all()

    assert len(framework_data) == 1
    assert len(framewok_section_data) == 1
    assert len(framework_control_objective_data) == 1

    assert framework_data[0].name == framework_name
    assert framewok_section_data[0].name == framework_section_name
    assert framework_control_objective_data[0].name == framework_control_objective_name
