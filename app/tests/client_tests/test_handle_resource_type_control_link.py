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


def test_handle_resource_type_control_creates_link_for_existing_resources(handler):
    ServiceFactory(id=10, name="Service One", reference="ref_1", type="NETWORK")
    res_type_1 = ResourceTypeFactory(
        id=20, name="res type one", reference="res-type-1", service_id=10
    )
    
    control = ControlFactory(
        id=99,
        name="testcontrol",
        quality_model=api_models.QualityModel.SECURITY,
        severity=api_models.ControlSeverity.LOW,
    )

    resource_type_control = handler.handle_resource_type_control_link(
        control, res_type_1
    )
    assert resource_type_control.control_id == 99
    assert resource_type_control.resource_type_id == 20

    data = db.session.query(ResourceTypeControl).all()
    assert len(data) == 1
    assert data[0].control_id == 99
    assert data[0].resource_type_id == 20
