# client.airviewclient package

## Submodules

## client.airviewclient.client module


### class client.airviewclient.client.Backend(backend_config, session)
Bases: `object`

Low level wrapper for calls to AirView api.
THIS CLASS IS INTENDED FOR INTERNAL USE ONLY.


#### \__init__(backend_config, session)

#### create_application(application, environment_id=None)
Create a new Application


* **Return type**

    `Application`



#### create_environment(environment)
Create a new environment


* **Return type**

    `Environment`



#### create_technical_control(technical_control)

* **Return type**

    `TechnicalControl`



#### get_application_by_reference(application_reference)
Look up an application by the provided reference


#### get_application_control_link(application_id, technical_control_id)
Get the id of application to control linkage


#### get_environments()
Get a list of environments


#### get_exclusion_resources(state)
Get a list of exclusion resources by state


#### get_technical_control(reference)
Get a Technical Control by its reference


* **Return type**

    `TechnicalControl`



#### get_url(route)
Helper method to resolve route to full url


* **Return type**

    `str`



#### link_application_to_control(application_id, technical_control_id)
create a new linkage between application and technical control


* **Return type**

    `int`



#### save_monitored_resource(app_tech_control_id, reference, state)
Persist the current status of a montiored resource


* **Return type**

    `None`



#### set_exclusion_resource_state(id, state)
Set the state of an exclusion resource


* **Return type**

    `None`



#### update_application(application, environment_id)

* **Return type**

    `None`



### class client.airviewclient.client.Handler(backend)
Bases: `object`

Main helper methods for interacting with AirView


#### \__init__(backend)

#### get_exclusions_by_state(state)
Get a list of exclusion resources filtered by state.


* **Parameters**

    **state** – The exclusion state to filter by



#### handle_application(application)
When passed an application definition, this method will attempt to create or update the application definintion.
Returns application with id present in response


* **Return type**

    `Application`



#### handle_compliance_event(compliance_event)
When passed a compliance event this method will attempt to create any missing defintions for Application and Technical Controls and persist the presented event


* **Return type**

    `None`



#### set_exclusion_resource_state(id, state)
Set the status of a exclusion resource


* **Parameters**

    
    * **id** (`int`) – The id of the exclusion resource to update


    * **state** (`ExclusionResourceState`) – The state to set the excusion to



* **Return type**

    `None`



### client.airviewclient.client.get_azure_token(client_id, client_secret, tenant_id, scope)
Helper method to get an Azure AD token for use with the client


* **Return type**

    `str`



### client.airviewclient.client.get_handler(base_url, system_id, referencing_type, token)
Get an instance of handler using the configuration provided


* **Parameters**

    
    * **base_url** (`str`) – The base url at which the AirView API is located


    * **system_id** (`int`) – The pre allocated id which will be used to uniquely identify this system in AirView


    * **referencing_type** (`str`) – The common reference type which will be used to identify/deduplicate applications e.g. aws_account_id


    * **token** (`str`) – The access token to be used to authenticate with the API



* **Return type**

    `Handler`


## client.airviewclient.models module


### class client.airviewclient.models.Application(name, reference, environment=None, type=1, id=None, parent_id=None)
Bases: `object`

Dataclass representing application definition


#### \__init__(name, reference, environment=None, type=1, id=None, parent_id=None)

#### environment(: Optional[client.airviewclient.models.Environment] = None)
Defintion of environment which the application sits in


#### id(: Optional[int] = None)
Internal identifier of application


#### name(: str)
Name of application


#### parent_id(: Optional[int] = None)
Internal id of parent application for nested apps


#### reference(: str)
Unique reference of application within the system. e.g. aws account id, azure subscription id


#### type(: int = 1)
ID for type of application.


### class client.airviewclient.models.BackendConfig(base_url, token, system_id, referencing_type)
Bases: `object`

Configuration data for connecting to a backend


#### \__init__(base_url, token, system_id, referencing_type)

#### base_url(: str)
Base url of the AirView api


#### referencing_type(: str)
Type of reference which will be used when identifying an application. e.g. aws_account_id


#### system_id(: int)
System id which is used to identify this integration with airview


#### token(: str)
Access token to be used when interacting with the backend


### exception client.airviewclient.models.BackendFailureException()
Bases: `Exception`


### class client.airviewclient.models.ComplianceEvent(resource_reference, application, technical_control, status)
Bases: `object`

Dataclass representing an incoming compliance event


#### \__init__(resource_reference, application, technical_control, status)

#### application(: client.airviewclient.models.Application)
Application within which the resource sits


#### resource_reference(: str)
Unique reference of the resource within the connecting system


#### status(: client.airviewclient.models.MonitoredResourceState)
The enum status of the event


#### technical_control(: client.airviewclient.models.TechnicalControl)
Technical control which this compliance event is the subject of


### class client.airviewclient.models.Environment(name, abbreviation, id=None)
Bases: `object`

Dataclass representing environment


#### \__init__(name, abbreviation, id=None)

#### abbreviation(: str)
Abbreviated name of the environment


#### id(: Optional[int] = None)
internal id for the environment


#### name(: str)
Name of environment


### class client.airviewclient.models.ExclusionResource(id, reference, technical_control_reference, application_reference, state)
Bases: `object`

Dataclass representing an exclusion resource


#### \__init__(id, reference, technical_control_reference, application_reference, state)

#### application_reference(: str)
unique reference for the application


#### id(: int)
Internal id of the exclusion resource


#### reference(: str)
Reference of the exclusion resource


#### state(: client.airviewclient.models.ExclusionResourceState)
status of the exclusion resource


#### technical_control_reference(: str)
unique reference for the technical control


### class client.airviewclient.models.ExclusionResourceState(value)
Bases: `enum.Enum`

An enumeration.


#### ACTIVE( = 3)

#### NONE( = 1)

#### PENDING( = 2)

### class client.airviewclient.models.MonitoredResourceState(value)
Bases: `enum.Enum`

An enumeration.


#### FIXED_AUTO( = 3)

#### FIXED_OTHER( = 4)

#### FLAGGED( = 1)

#### SUPPRESSED( = 2)

### class client.airviewclient.models.QualityModel(value)
Bases: `enum.Enum`

An enumeration.


#### COST_OPTIMISATION( = 5)

#### OPERATIONAL_EXCELLENCE( = 1)

#### PERFORMANCE_EFFICIENCY( = 4)

#### PORTABILITY( = 6)

#### RELIABILITY( = 3)

#### SECURITY( = 2)

#### USABILITY_AND_COMPATIBILITY( = 7)

### class client.airviewclient.models.TechnicalControl(name, reference, quality_model, type, id=None)
Bases: `object`

Dataclass representing technical control definition


#### \__init__(name, reference, quality_model, type, id=None)

#### id(: Optional[int] = None)
Internal id of the techincal control


#### name(: str)
The name of the technical control


#### quality_model(: client.airviewclient.models.QualityModel)
Quality model of the techincal control


#### reference(: str)
Unique reference for the control within the connecting system


#### type(: client.airviewclient.models.TechnicalControlType)
Type of control


### class client.airviewclient.models.TechnicalControlType(value)
Bases: `enum.Enum`

An enumeration.


#### OPERATIONAL( = 2)

#### SECURITY( = 1)

#### TASK( = 3)
## Module contents
