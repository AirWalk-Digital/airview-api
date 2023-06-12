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


@pytest.fixture()
def technical_control():
    technical_control = models.TechnicalControl(
        name="ctrl a",
        reference="tc-ref-1",
        is_blocking=True,
        ttl=20,
        control_action=models.TechnicalControlAction.LOG,
    )

    yield technical_control


def setup():
    setup_factories()


def test_technical_control_creates_missing(handler, technical_control):
    
    """
    Given: A technical control which is not findable within the api
    When: When a call is made to persist a technical control
    Then: A new technical control is created
    """
    # Arrange

    SystemFactory(id=111, stage=api_models.SystemStage.BUILD, name="one")
    TechnicalControlFactory(
        id=999,
        reference="tc-ref-other",
        name="one",
        system_id=111,
        control_action=TechnicalControlAction.LOG,
    )
    # Act
    returned_technical_control = handler.handle_technical_control(technical_control)

    # Assert
    technical_controls = TechnicalControl.query.all()
    assert len(technical_controls) == 2
    assert technical_controls[1].id == 1000
    assert technical_controls[1].reference == "tc-ref-1"
    assert technical_controls[1].name == "ctrl a"
    assert technical_controls[1].is_blocking == True
    assert technical_controls[1].control_action == api_models.TechnicalControlAction.LOG

    assert returned_technical_control.id == 1000
    assert returned_technical_control.reference == "tc-ref-1"
    assert returned_technical_control.name == "ctrl a"
    assert returned_technical_control.is_blocking == True
    assert returned_technical_control.control_action == models.TechnicalControlAction.LOG

def test_technical_control_finds_existing(handler, technical_control):
    
    """
    Given: A technical control which is present in the api
    When: When a call is made to persist a technical control
    Then: The existing technical control is returned and the existing control is not updated
    """
    # Arrange

    SystemFactory(id=111, stage=api_models.SystemStage.BUILD, name="one")
    TechnicalControlFactory(
        id=999,
        reference="tc-ref-other",
        name="one",
        system_id=111,
        control_action=TechnicalControlAction.LOG,
    )
    TechnicalControlFactory(
        id=1000,
        reference="tc-ref-1",
        is_blocking=False,
        name="one",
        system_id=111,
        control_action=TechnicalControlAction.INCIDENT,
    )
    # Act
    returned_technical_control = handler.handle_technical_control(technical_control)

    # Assert
    technical_controls = TechnicalControl.query.all()
    assert len(technical_controls) == 2
    assert technical_controls[1].id == 1000
    assert technical_controls[1].reference == "tc-ref-1"
    assert technical_controls[1].name == "one"
    assert technical_controls[1].is_blocking == False
    assert technical_controls[1].control_action == api_models.TechnicalControlAction.INCIDENT

    assert returned_technical_control.id == 1000
    assert returned_technical_control.reference == "tc-ref-1"
    assert returned_technical_control.name == "one"
    assert returned_technical_control.is_blocking == False
    assert returned_technical_control.control_action == models.TechnicalControlAction.INCIDENT
