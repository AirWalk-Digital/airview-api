# client.airviewclient package

## Submodules

## client.airviewclient.client module


### _class_ client.airviewclient.client.Backend(backend_config, session)
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



#### create_system(name, stage)
Create a new system


* **Return type**

    `Environment`



#### create_technical_control(technical_control)

* **Return type**

    `TechnicalControl`



#### get_application_by_reference(application_reference)
Look up an application by the provided reference


* **Return type**

    Application | None



#### get_application_control_link(application_id, technical_control_id)
Get the id of application to control linkage


* **Return type**

    int | None



#### get_environments()
Get a list of environments


#### get_exclusion_resources(state)
Get a list of exclusion resources by state


#### get_system_id_by_name(name)

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



#### save_monitored_resource(app_tech_control_id, reference, state, type)
Persist the current status of a montiored resource


* **Return type**

    `None`



#### set_exclusion_resource_state(id, state)
Set the state of an exclusion resource


* **Return type**

    `None`



#### _property_ system_id()

#### update_application(application, environment_id)

* **Return type**

    `None`



### _class_ client.airviewclient.client.Handler(backend)
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



### client.airviewclient.client.get_handler(base_url, system_name, system_stage, referencing_type, token)
Get an instance of handler using the configuration provided


* **Parameters**


    * **base_url** (`str`) – The base url at which the AirView API is located


    * **system_name** (`str`) – The unique name which identifies this system


    * **referencing_type** (`str`) – The common reference type which will be used to identify/deduplicate applications e.g. aws_account_id


    * **token** (`str`) – The access token to be used to authenticate with the API



* **Return type**

    `Handler`


## client.airviewclient.models module


### _class_ client.airviewclient.models.Application(name, reference, type=ApplicationType.BUSINESS_APPLICATION, environment=None, id=None, parent_id=None)
Bases: `object`

Dataclass representing application definition


#### \__init__(name, reference, type=ApplicationType.BUSINESS_APPLICATION, environment=None, id=None, parent_id=None)

#### environment(_: Optional[Environment_ _ = Non_ )
Defintion of environment which the application sits in


#### id(_: Optional[int_ _ = Non_ )
Internal identifier of application


#### name(_: st_ )
Name of application


#### parent_id(_: Optional[int_ _ = Non_ )
Internal id of parent application for nested apps


#### reference(_: st_ )
Unique reference of application within the system. e.g. aws account id, azure subscription id


#### type(_: ApplicationTyp_ _ = _ )
Type of application.


### _class_ client.airviewclient.models.ApplicationType(value)
Bases: `Enum`

An enumeration.


#### APPLICATION_SERVICE(_ = _ )

#### BUSINESS_APPLICATION(_ = _ )

#### TECHNICAL_SERVICE(_ = _ )

### _class_ client.airviewclient.models.BackendConfig(base_url, token, system_name, system_stage, referencing_type)
Bases: `object`

Configuration data for connecting to a backend


#### \__init__(base_url, token, system_name, system_stage, referencing_type)

#### base_url(_: st_ )
Base url of the AirView api


#### referencing_type(_: st_ )
Type of reference which will be used when identifying an application. e.g. aws_account_id


#### system_name(_: st_ )
Unique name which identifies this system


#### system_stage(_: SystemStag_ )
Stage at which this instance monitors


#### token(_: st_ )
Access token to be used when interacting with the backend


### _exception_ client.airviewclient.models.BackendFailureException()
Bases: `Exception`


### _class_ client.airviewclient.models.ComplianceEvent(resource_reference, application, technical_control, status, type, additional_data='')
Bases: `object`

Dataclass representing an incoming compliance event


#### \__init__(resource_reference, application, technical_control, status, type, additional_data='')

#### additional_data(_: st_ _ = '_ )
Any additional textual data to associate with the event


#### application(_: Applicatio_ )
Application within which the resource sits


#### resource_reference(_: st_ )
Unique reference of the resource within the connecting system


#### status(_: MonitoredResourceStat_ )
The enum status of the event


#### technical_control(_: TechnicalContro_ )
Technical control which this compliance event is the subject of


#### type(_: MonitoredResourceTyp_ )
The enum of the resource type


### _class_ client.airviewclient.models.Environment(name, abbreviation, id=None)
Bases: `object`

Dataclass representing environment


#### \__init__(name, abbreviation, id=None)

#### abbreviation(_: st_ )
Abbreviated name of the environment


#### id(_: Optional[int_ _ = Non_ )
internal id for the environment


#### name(_: st_ )
Name of environment


### _class_ client.airviewclient.models.ExclusionResource(id, reference, technical_control_reference, application_reference, state)
Bases: `object`

Dataclass representing an exclusion resource


#### \__init__(id, reference, technical_control_reference, application_reference, state)

#### application_reference(_: st_ )
unique reference for the application


#### id(_: in_ )
Internal id of the exclusion resource


#### reference(_: st_ )
Reference of the exclusion resource


#### state(_: ExclusionResourceStat_ )
status of the exclusion resource


#### technical_control_reference(_: st_ )
unique reference for the technical control


### _class_ client.airviewclient.models.ExclusionResourceState(value)
Bases: `Enum`

An enumeration.


#### ACTIVE(_ = _ )

#### NONE(_ = _ )

#### PENDING(_ = _ )

### _class_ client.airviewclient.models.MonitoredResourceState(value)
Bases: `Enum`

An enumeration.


#### FIXED_AUTO(_ = _ )

#### FIXED_OTHER(_ = _ )

#### FLAGGED(_ = _ )

#### SUPPRESSED(_ = _ )

### _class_ client.airviewclient.models.MonitoredResourceType(value)
Bases: `Enum`

An enumeration.


#### CONTAINER(_ = _ )

#### DATABASE(_ = _ )

#### FUNCTION(_ = _ )

#### NETWORK(_ = _ )

#### OBJECT_STORAGE(_ = _ )

#### PIPELINE(_ = _ )

#### REPOSITORY(_ = _ )

#### STORAGE(_ = 1_ )

#### VIRTUAL_MACHINE(_ = _ )

### _class_ client.airviewclient.models.QualityModel(value)
Bases: `Enum`

An enumeration.


#### COST_OPTIMISATION(_ = _ )

#### LOG_EXCELLENCE(_ = _ )

#### PERFORMANCE_EFFICIENCY(_ = _ )

#### PORTABILITY(_ = _ )

#### RELIABILITY(_ = _ )

#### SECURITY(_ = _ )

#### USABILITY_AND_COMPATIBILITY(_ = _ )

### _class_ client.airviewclient.models.SystemStage(value)
Bases: `Enum`

An enumeration.


#### BUILD(_ = _ )

#### MONITOR(_ = _ )

### _class_ client.airviewclient.models.TechnicalControl(name, reference, quality_model, type, id=None, parent_id=None, ttl=None, is_blocking=None, can_delete_resources=None)
Bases: `object`

Dataclass representing technical control definition


#### \__init__(name, reference, quality_model, type, id=None, parent_id=None, ttl=None, is_blocking=None, can_delete_resources=None)

#### can_delete_resources(_: Optional[bool_ _ = Non_ )
Can resources be unlinked from the control


#### id(_: Optional[int_ _ = Non_ )
Internal id of the techincal control


#### is_blocking(_: Optional[bool_ _ = Non_ )
Should a failure cause a process to exit


#### name(_: st_ )
The name of the technical control


#### parent_id(_: Optional[int_ _ = Non_ )
Id of parent control


#### quality_model(_: QualityMode_ )
Quality model of the techincal control


#### reference(_: st_ )
Unique reference for the control within the connecting system


#### ttl(_: Optional[int_ _ = Non_ )
Period after which the control should be assumed non compliant


#### type(_: TechnicalControlTyp_ )
Type of control


### _class_ client.airviewclient.models.TechnicalControlType(value)
Bases: `Enum`

An enumeration.


#### LOG(_ = _ )

#### SECURITY(_ = _ )

#### TASK(_ = _ )

#### VULNERABILITY(_ = _ )
## Module contents
