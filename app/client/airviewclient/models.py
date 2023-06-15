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


class TechnicalControlAction(Enum):
    LOG = 1
    INCIDENT = 2
    TASK = 3
    VULNERABILITY = 4

    def __str__(self):
        return self.name


class SystemStage(Enum):
    BUILD = 1
    MONITOR = 2

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


@dataclass
class BackendConfig:
    """Configuration data for connecting to a backend"""

    #: Base url of the AirView api
    base_url: str
    #: Access token to be used when interacting with the backend
    token: str
    #: Unique name which identifies this system
    system_name: str
    #: Stage at which this instance monitors
    system_stage: SystemStage
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
    #: Type of application.
    type: ApplicationType = ApplicationType.BUSINESS_APPLICATION
    #: Defintion of environment which the application sits in
    environment: Environment = Environment(name="Unknown", abbreviation="UNK")
    #: Internal identifier of application
    id: Optional[int] = None
    #: Internal id of application environment
    application_environment_id: Optional[int] = None


@dataclass
class TechnicalControl:
    """Dataclass representing technical control definition"""

    #: The name of the technical control
    name: str
    #: Unique reference for the control within the connecting system
    reference: str
    #: Type of control
    control_action: TechnicalControlAction
    #: Id of control
    id: Optional[int] = None
    #: Id of parent control
    ttl: Optional[int] = None
    #: Should a failure cause a process to exit
    is_blocking: Optional[bool] = None


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
    #: Any additional textual data to associate with the event
    additional_data: str = ""


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


@dataclass
class Service:
    """Dataclass representing a service"""

    #: Unique reference of the service within the connecting system
    reference: str
    #: A friendly name for the service
    name: str
    #: The type of service this is
    type: ServiceType
    #: Internal identifier of service
    id: Optional[int] = None


@dataclass
class Resource:
    """Dataclass representing an resource"""

    #: Unique reference of the resource within the connecting system
    reference: str
    #: A friendly name for the resource
    name: str
    #: Application within which the resource sits
    application: Application
    #: The service which this resource belongs to (ec2, s3, dynamodb, etc)
    service: Service


class BackendFailureException(Exception):
    pass
