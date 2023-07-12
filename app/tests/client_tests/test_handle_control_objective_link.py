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


def test_handle_control_objective_link_creates_link(handler):
    framework = FrameworkFactory(
        name="TestFramework",
        link="/testframework"
    )

    framework_section = FrameworkSectionFactory(
        name="TestFrameworkSection",
        link="/testframework/testsection",
        framework_id=1
    )
    framework_section.framework = framework

    framework_control_objective = FrameworkControlObjectiveFactory(
        name="AC-12",
        link="/testframework/testsection/ac-12",
        framework_section_id=1
    )
    framework_control_objective.framework_section = framework_section
    
    ServiceFactory(id=1, name="Service One", reference="ref_1", type="NETWORK")

    control = ControlFactory(
        name="testcontrol",
        quality_model=api_models.QualityModel.SECURITY,
        service_id=1,
        severity=api_models.ControlSeverity.LOW
    )

    control.id = None
    framework_control_objective.id = None

    handler.handle_framework_control_objective_link(
        framework_control_objective, control
    )
