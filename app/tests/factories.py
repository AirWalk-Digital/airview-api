import factory
from airview_api.models import (
    TechnicalControl,
    System,
    Application,
    ApplicationType,
    Environment,
    ApplicationTechnicalControl,
    MonitoredResource,
    Exclusion,
    ApplicationReference,
    QualityModel,
    TechnicalControlAction,
    MonitoredResourceType,
)
from airview_api.database import db


class TechnicalControlFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TechnicalControl
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"TC {n}")

    control_action = TechnicalControlAction.LOG
    quality_model = QualityModel.COST_OPTIMISATION
    is_blocking = False
    can_delete_resources = True


class SystemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = System
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"System {n}")


class ApplicationReferenceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ApplicationReference
        sqlalchemy_session = db.session


class ApplicationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Application
        sqlalchemy_session = db.session

    name = factory.Sequence(lambda n: f"App {n}")
    application_type = ApplicationType.BUSINESS_APPLICATION


class EnvironmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Environment
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Env {n}")
    abbreviation = factory.Sequence(lambda n: f"E{n}")


class ApplicationTechnicalControlFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ApplicationTechnicalControl
        sqlalchemy_session = db.session


class MonitoredResourceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = MonitoredResource
        sqlalchemy_session = db.session

    type = MonitoredResourceType.VIRTUAL_MACHINE


class ExclusionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Exclusion
        sqlalchemy_session = db.session


def reset_factories():
    TechnicalControlFactory.reset_sequence()
    SystemFactory.reset_sequence()
    ApplicationFactory.reset_sequence()
    EnvironmentFactory.reset_sequence()
    ApplicationTechnicalControlFactory.reset_sequence()
    MonitoredResourceFactory.reset_sequence()
    ExclusionFactory.reset_sequence()
    MonitoredResourceFactory.reset_sequence()
