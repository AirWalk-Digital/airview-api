from datetime import timezone
from enum import Enum
from airview_api.database import db


class TechnicalControlSeverity(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

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
    SUPPRESSED = 2
    FIXED_AUTO = 3
    FIXED_OTHER = 4

    def __str__(self):
        return self.name


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    application_type_id = db.Column(
        db.Integer, db.ForeignKey("application_type.id"), nullable=False
    )
    application_type = db.relationship(
        "ApplicationType", back_populates="applications", lazy=True
    )
    environment_id = db.Column(
        db.Integer, db.ForeignKey("environment.id"), nullable=True
    )
    parent_id = db.Column(db.Integer, db.ForeignKey("application.id"), nullable=True)
    children = db.relationship(
        "Application", backref=db.backref("parent", remote_side=[id])
    )
    environment = db.relationship("Environment", back_populates="applications")
    application_technical_controls = db.relationship(
        "ApplicationTechnicalControl",
        back_populates="application",
    )
    references = db.relationship(
        "ApplicationReference", back_populates="application", lazy="dynamic"
    )

    def __repr__(self):
        return f"{self.name}"


class ApplicationReference(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False,
    )

    type = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(500), nullable=False)
    __table_args__ = (
        db.UniqueConstraint(
            "type",
            "reference",
            name="uq_application_reference",
        ),
        db.UniqueConstraint(
            "application_id",
            "type",
            name="uq_application_type",
        ),
    )

    application = db.relationship("Application", back_populates="references")


class ApplicationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    applications = db.relationship(
        "Application", back_populates="application_type", lazy=True
    )

    def __repr__(self):
        return f"{self.name}"


class Environment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    abbreviation = db.Column(db.String(10), nullable=False)
    applications = db.relationship(
        "Application", back_populates="environment", lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "abbreviation",
            name="uq_environment",
        ),
    )

    def __repr__(self):
        return f"{self.name}"


class TechnicalControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(500), nullable=False)
    control_type_id = db.Column(db.Integer, nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey("system.id"), nullable=False)
    severity = db.Column(db.Enum(TechnicalControlSeverity), nullable=False)

    application_technical_controls = db.relationship(
        "ApplicationTechnicalControl",
        back_populates="technical_control",
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
    source = db.Column(db.String(500), nullable=True)
    stage = db.Column(db.String(50), nullable=True)
    technical_controls = db.relationship("TechnicalControl", back_populates="system")

    def __repr__(self):
        return f"{self.name}"


class MonitoredResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(500), nullable=False)
    state = db.Column(db.Enum(MonitoredResourceState), nullable=False)
    last_modified = db.Column(db.DateTime(timezone=True), nullable=False)
    last_seen = db.Column(db.DateTime(timezone=True), nullable=False)

    application_technical_control_id = db.Column(
        db.Integer,
        db.ForeignKey("application_technical_control.id"),
        nullable=False,
    )
    application_technical_control = db.relationship(
        "ApplicationTechnicalControl", back_populates="monitored_resources"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "application_technical_control_id",
            "reference",
            name="uq_monitored_resource",
        ),
    )


class ApplicationTechnicalControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer, db.ForeignKey("application.id"), nullable=False
    )
    technical_control_id = db.Column(
        db.Integer, db.ForeignKey("technical_control.id"), nullable=False
    )

    application = db.relationship(
        "Application", back_populates="application_technical_controls"
    )
    technical_control = db.relationship(
        "TechnicalControl", back_populates="application_technical_controls"
    )

    monitored_resources = db.relationship(
        "MonitoredResource",
        back_populates="application_technical_control",
        lazy=True,
        cascade="delete",
    )

    exclusions = db.relationship(
        "Exclusion",
        back_populates="application_technical_control",
        lazy=True,
        cascade="delete",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "application_id",
            "technical_control_id",
            name="uq_application_technical_control",
        ),
    )

    def __repr__(self):
        return f"{self.application.name} {self.technical_control.name}"


class Exclusion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_technical_control_id = db.Column(
        db.Integer,
        db.ForeignKey("application_technical_control.id"),
        nullable=False,
    )
    summary = db.Column(db.String, nullable=False)
    mitigation = db.Column(db.String, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Integer, nullable=False)
    is_limited_exclusion = db.Column(db.Boolean, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String, nullable=True)
    application_technical_control = db.relationship(
        "ApplicationTechnicalControl", back_populates="exclusions"
    )
    resources = db.relationship("ExclusionResource", back_populates="exclusion")


class ExclusionResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exclusion_id = db.Column(
        db.Integer,
        db.ForeignKey("exclusion.id"),
        nullable=False,
    )
    exclusion = db.relationship("Exclusion", back_populates="resources")

    reference = db.Column(db.String, nullable=False)
    state = db.Column(db.Enum(ExclusionState), nullable=False)


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


class TechnicalControlType(Enum):
    SECURITY = 1
    OPERATIONAL = 2
    TASK = 3
