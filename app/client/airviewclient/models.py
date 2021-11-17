from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ExclusionResourceState(Enum):
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


class QualityModel(Enum):
    OPERATIONAL_EXCELLENCE = 1
    SECURITY = 2
    RELIABILITY = 3
    PERFORMANCE_EFFICIENCY = 4
    COST_OPTIMISATION = 5
    PORTABILITY = 6
    USABILITY_AND_COMPATIBILITY = 7

    def __str__(self):
        return self.name


@dataclass
class BackendConfig:
    """Configuration data for connecting to a backend"""

    #: Base url of the AirView api
    base_url: str
    #: Access token to be used when interacting with the backend
    token: str
    #: System id which is used to identify this integration with airview
    system_id: int
    #: Type of reference which will be used when identifying an application. e.g. aws_account_id
    referencing_type: str


@dataclass
class Environment:
    """Dataclass representing environment"""

    #: Name of environment
    name: str
    #: Abbreviated name of the environment
    abbreviation: str
    #: internal id for the environment
    id: Optional[int] = None


@dataclass
class Application:
    """Dataclass representing application definition"""

    #: Name of application
    name: str
    #: Unique reference of application within the system. e.g. aws account id, azure subscription id
    reference: str
    #: Defintion of environment which the application sits in
    environment: Optional[Environment] = None
    #: ID for type of application.
    type: int = 1
    #: Internal identifier of application
    id: Optional[int] = None
    #: Internal id of parent application for nested apps
    parent_id: Optional[int] = None


@dataclass
class TechnicalControl:
    """Dataclass representing technical control definition"""

    #: The name of the technical control
    name: str
    #: Unique reference for the control within the connecting system
    reference: str
    #:Quality model of the techincal control
    quality_model: QualityModel
    #: Id for type of control
    type: int = 1
    #: Internal id of the techincal control
    id: Optional[int] = None


@dataclass
class ComplianceEvent:
    """Dataclass representing an incoming compliance event"""

    #: Unique reference of the resource within the connecting system
    resource_reference: str
    #: Application within which the resource sits
    application: Application
    #: Technical control which this compliance event is the subject of
    technical_control: TechnicalControl
    #: The enum status of the event
    status: MonitoredResourceState


@dataclass
class ExclusionResource:
    """Dataclass representing an exclusion resource"""

    #: Internal id of the exclusion resource
    id: int
    #: Reference of the exclusion resource
    reference: str
    #: unique reference for the technical control
    technical_control_reference: str
    #: unique reference for the application
    application_reference: str
    #: status of the exclusion resource
    state: ExclusionResourceState


class BackendFailureException(Exception):
    pass
