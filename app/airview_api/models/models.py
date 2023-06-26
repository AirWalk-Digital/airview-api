from enum import Enum
from airview_api.database import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case


class ControlSeverity(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

    def __str__(self):
        return self.name


class SystemStage(Enum):
    BUILD = 1
    MONITOR = 2

    def __str__(self):
        return self.name


class ExclusionState(Enum):
    NONE = 1
    PENDING = 2
    ACTIVE = 3

    def __str__(self):
        return self.name


class MonitoredResourceState(Enum):
    FLAGGED = 1
    MONITORING = 2
    DELETED = 3

    def __str__(self):
        return self.name


class QualityModel(Enum):
    LOG_EXCELLENCE = 1
    SECURITY = 2
    RELIABILITY = 3
    PERFORMANCE_EFFICIENCY = 4
    COST_OPTIMISATION = 5
    PORTABILITY = 6
    USABILITY_AND_COMPATIBILITY = 7

    def __str__(self):
        return self.name


class ApplicationType(Enum):
    BUSINESS_APPLICATION = 1
    TECHNICAL_SERVICE = 2
    APPLICATION_SERVICE = 3

    def __str__(self):
        return self.name


class ServiceType(Enum):
    UNKNOWN = 1
    VIRTUAL_MACHINE = 2
    CONTAINER = 3
    NETWORK = 4
    REPOSITORY = 5
    PIPELINE = 6
    OBJECT_STORAGE = 7
    DATABASE = 8
    FUNCTION = 9
    STORAGE = 10

    def __str__(self):
        return self.name


class TechnicalControlAction(Enum):
    LOG = 1
    INCIDENT = 2
    TASK = 3
    VULNERABILITY = 4

    def __str__(self):
        return self.name


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    application_type = db.Column(db.Enum(ApplicationType), nullable=False)

    application_environments = db.relationship(
        "ApplicationEnvironment", back_populates="application"
    )

    def __repr__(self):
        return f"{self.name}"


class ApplicationEnvironment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    application_id = db.Column(
        db.Integer, db.ForeignKey("application.id"), nullable=False
    )
    environment_id = db.Column(
        db.Integer, db.ForeignKey("environment.id"), nullable=True
    )

    application = db.relationship(
        "Application", back_populates="application_environments"
    )
    environment = db.relationship(
        "Environment", back_populates="application_environments"
    )
    references = db.relationship(
        "ApplicationEnvironmentReference",
        back_populates="application_environment",
        lazy="dynamic",
    )
    resources = db.relationship(
        "Resource", back_populates="application_environment", lazy="dynamic"
    )

    exclusions = db.relationship(
        "Exclusion", back_populates="application_environment", lazy="dynamic"
    )

    def __repr__(self):
        return f"{self.name}"


class ApplicationEnvironmentReference(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    application_environment_id = db.Column(
        db.Integer,
        db.ForeignKey("application_environment.id"),
        nullable=False,
    )

    type = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(500), nullable=False)
    __table_args__ = (
        db.UniqueConstraint(
            "type",
            "reference",
            name="uq_application_enviroinment_reference",
        ),
        db.UniqueConstraint(
            "application_environment_id",
            "type",
            name="uq_application_environment_type",
        ),
    )

    application_environment = db.relationship(
        "ApplicationEnvironment", back_populates="references"
    )


class Environment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    abbreviation = db.Column(db.String(10), nullable=False)
    application_environments = db.relationship(
        "ApplicationEnvironment", back_populates="environment", lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "abbreviation",
            name="uq_environment",
        ),
    )

    def __repr__(self):
        return f"{self.name}"


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(500), nullable=False)
    type = db.Column(db.Enum(ServiceType), nullable=False)

    controls = db.relationship("Control", back_populates="service")
    resources = db.relationship("Resource", back_populates="service")

    __table_args__ = (
        db.UniqueConstraint(
            "reference",
            name="uq_service",
        ),
    )


class FrameworkControlObjectiveLink(db.Model):
    framework_control_objective_id = db.Column(
        db.Integer,
        db.ForeignKey("framework_control_objective.id"),
        primary_key=True,
    )
    control_id = db.Column(
        db.Integer,
        db.ForeignKey("control.id"),
        primary_key=True,
    )


class FrameworkControlObjective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500), nullable=False)
    framework_section_id = db.Column(
        db.Integer,
        db.ForeignKey("framework_section.id"),
    )

    controls = db.relationship(
        "Control",
        secondary=FrameworkControlObjectiveLink.__table__,
        back_populates="framework_control_objectives",
        primaryjoin=id
        == FrameworkControlObjectiveLink.framework_control_objective_id,  # Update this line
        secondaryjoin=id == FrameworkControlObjectiveLink.control_id,
    )
    framework_section = db.relationship(
        "FrameworkSection", back_populates="framework_control_objectives"
    )


class FrameworkSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    framework_id = db.Column(
        db.Integer,
        db.ForeignKey("framework.id"),
    )
    framework = db.relationship("Framework", back_populates="framework_sections")
    framework_control_objectives = db.relationship(
        "FrameworkControlObjective", back_populates="framework_section"
    )


class Framework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=False)

    framework_sections = db.relationship("FrameworkSection", back_populates="framework")


class Control(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    quality_model = db.Column(db.Enum(QualityModel), nullable=False)
    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
    )
    severity = db.Column(db.Enum(ControlSeverity), nullable=False)

    service = db.relationship("Service", back_populates="controls")

    exclusions = db.relationship("Exclusion", back_populates="control", lazy="dynamic")

    technical_controls = db.relationship("TechnicalControl", back_populates="control")

    framework_control_objectives = db.relationship(
        "FrameworkControlObjective",
        secondary=FrameworkControlObjectiveLink.__table__,
        back_populates="controls",
        primaryjoin=id == FrameworkControlObjectiveLink.control_id,  # Update this line
        secondaryjoin=id
        == FrameworkControlObjectiveLink.framework_control_objective_id,
    )


class TechnicalControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(500), nullable=False)
    control_action = db.Column(db.Enum(TechnicalControlAction), nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey("system.id"), nullable=False)
    ttl = db.Column(db.Integer, nullable=True)
    is_blocking = db.Column(db.Boolean, nullable=False)

    control_id = db.Column(db.Integer, db.ForeignKey("control.id"), nullable=True)

    control = db.relationship("Control", back_populates="technical_controls")

    monitored_resources = db.relationship(
        "MonitoredResource", back_populates="technical_control"
    )

    system = db.relationship("System", back_populates="technical_controls")

    __table_args__ = (
        db.UniqueConstraint(
            "system_id",
            "reference",
            name="uq_technical_control",
        ),
    )

    def __repr__(self):
        return f"{self.name}"


class System(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    stage = db.Column(db.Enum(SystemStage), nullable=False)
    technical_controls = db.relationship("TechnicalControl", back_populates="system")

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            name="uq_system",
        ),
    )

    def __repr__(self):
        return f"{self.name}"


class ExclusionResource(db.Model):
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"), primary_key=True)
    exclusion_id = db.Column(
        db.Integer, db.ForeignKey("exclusion.id"), primary_key=True
    )


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(500), nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False)
    last_seen = db.Column(db.DateTime, nullable=False)
    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=True,
    )
    service = db.relationship("Service", back_populates="resources")

    application_environment_id = db.Column(
        db.Integer,
        db.ForeignKey("application_environment.id"),
        nullable=True,
    )
    application_environment = db.relationship(
        "ApplicationEnvironment", back_populates="resources"
    )

    monitored_resources = db.relationship(
        "MonitoredResource", back_populates="resource"
    )
    exclusions = db.relationship(
        "Exclusion", secondary=ExclusionResource.__table__, back_populates="resources"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "reference",
            "application_environment_id",
            name="uq_resource",
        ),
    )


class MonitoredResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resource.id"),
        nullable=False,
    )

    resource = db.relationship("Resource", back_populates="monitored_resources")
    monitoring_state = db.Column(db.Enum(MonitoredResourceState), nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False)
    last_seen = db.Column(db.DateTime, nullable=True)
    additional_data = db.Column(db.String(8000), nullable=False, default="")

    technical_control_id = db.Column(
        db.Integer,
        db.ForeignKey("technical_control.id"),
        nullable=False,
    )
    technical_control = db.relationship(
        "TechnicalControl", back_populates="monitored_resources"
    )


""" This needs looking at again post 'hackathon'
    @hybrid_property
    def state(self):
        return (
            MonitoredResourceState.SUPPRESSED
            if self.exclusion_state == ExclusionState.ACTIVE
            else self.monitoring_state
        )

    @state.expression
    def state(cls):
        return case(
            {"ACTIVE": MonitoredResourceState.SUPPRESSED.name},
            cls.exclusion_state,
            cls.monitoring_state,
        )
"""

# __table_args__ = (
# db.UniqueConstraint(
# "application_technical_control_id",
# "resource_id",
# name="uq_monitored_resource",
# ),
# )


# class MonitoredResourceTicket(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     monitored_resource_id = db.Column(
#         db.Integer,
#         db.ForeignKey("monitored_resource.id"),
#         nullable=False,
#     )
#     reference = db.Column(db.String(50), nullable=True)
#     request_timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
#     monitored_resource = db.relationship("MonitoredResource", back_populates="tickets")


class Exclusion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String, nullable=False)
    is_limited_exclusion = db.Column(db.Boolean, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String, nullable=True)
    status = db.Column(db.Enum(ExclusionState), nullable=True)

    control_id = db.Column(
        db.Integer,
        db.ForeignKey("control.id"),
        nullable=False,
    )
    control = db.relationship("Control", back_populates="exclusions")
    application_environment_id = db.Column(
        db.Integer,
        db.ForeignKey("application_environment.id"),
        nullable=True,
    )
    application_environment = db.relationship(
        "ApplicationEnvironment", back_populates="exclusions"
    )

    resources = db.relationship(
        "Resource", secondary=ExclusionResource.__table__, back_populates="exclusions"
    )


class NamedUrl:
    def __init__(self, name, url):
        self.name = name
        self.url = url


class ControlStatusDetail:
    def __init__(
        self, id, application_name, control, frameworks, assignment_group, assignee
    ):
        self.id = id
        self.application_name = application_name
        self.control = control
        self.frameworks = frameworks
        self.assignment_group = assignment_group
        self.assignee = assignee
