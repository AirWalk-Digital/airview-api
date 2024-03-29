import factory
from airview_api.models import (
    TechnicalControl,
    System,
    Application,
    ApplicationType,
    Environment,
    MonitoredResource,
    Exclusion,
    ApplicationEnvironmentReference,
    ApplicationEnvironment,
    QualityModel,
    Service,
    Resource,
    ResourceType,
    TechnicalControlAction,
    Framework,
    FrameworkControlObjective,
    FrameworkControlObjectiveLink,
    FrameworkSection,
    Control,
    ResourceTypeControl
)
from airview_api.database import db
from datetime import datetime


class TechnicalControlFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TechnicalControl
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"TC {n}")

    is_blocking = False
    control_action = TechnicalControlAction.LOG


class ControlFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Control
        sqlalchemy_session = db.session


class ServiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Service
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Service {n}")


class SystemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = System
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"System {n}")


class ApplicationEnvironmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ApplicationEnvironment
        sqlalchemy_session = db.session


class ApplicationEnvironmentReferenceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ApplicationEnvironmentReference
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


# class ApplicationTechnicalControlFactory(factory.alchemy.SQLAlchemyModelFactory):
# class Meta:
# model = ApplicationTechnicalControl
# sqlalchemy_session = db.session


class ResourceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Resource
        sqlalchemy_session = db.session

    last_seen = datetime.utcnow()
    last_modified = datetime.utcnow()


class MonitoredResourceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = MonitoredResource
        sqlalchemy_session = db.session


class FrameworkFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Framework
        sqlalchemy_session = db.session


class FrameworkControlObjectiveFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FrameworkControlObjective
        sqlalchemy_session = db.session


class FrameworkControlObjectiveLinkFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FrameworkControlObjectiveLink
        sqlalchemy_session = db.session


class FrameworkSectionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FrameworkSection
        sqlalchemy_session = db.session


class ExclusionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Exclusion
        sqlalchemy_session = db.session


class ResourceTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ResourceType
        sqlalchemy_session = db.session


class ResourceTypeControlFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ResourceTypeControl
        sqlalchemy_session = db.session


def reset_factories():
    TechnicalControlFactory.reset_sequence()
    SystemFactory.reset_sequence()
    ServiceFactory.reset_sequence()
    ApplicationFactory.reset_sequence()
    ApplicationEnvironmentFactory.reset_sequence()
    ApplicationEnvironmentReferenceFactory.reset_sequence()
    EnvironmentFactory.reset_sequence()
    # ApplicationTechnicalControlFactory.reset_sequence()
    MonitoredResourceFactory.reset_sequence()
    ExclusionFactory.reset_sequence()
    MonitoredResourceFactory.reset_sequence()
    ResourceFactory.reset_sequence()
    ResourceTypeFactory.reset_sequence()
    FrameworkFactory.reset_sequence()
    FrameworkControlObjectiveFactory.reset_sequence()
    FrameworkControlObjectiveLinkFactory.reset_sequence()
    FrameworkSectionFactory.reset_sequence()
