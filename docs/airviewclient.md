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



#### create_application_environment(application)
Create a new Application Environment, returns application environment id


* **Return type**

    `Application`



#### create_control(control)

* **Return type**

    `Control`



#### create_environment(environment)
Create a new environment


* **Return type**

    `Environment`



#### create_framework(framework)

* **Return type**

    `Optional`[`Framework`]



#### create_framework_control_objective(framework_control_objective)

* **Return type**

    `Optional`[`FrameworkControlObjective`]



#### create_framework_control_objective_link(framework_control_objective, control)

* **Return type**

    `Optional`[`FrameworkControlObjectiveLink`]



#### create_framework_section(framework_section)

* **Return type**

    `Optional`[`FrameworkSection`]



#### create_resource(reference, application_environment_id)
Create a barebone resource for linking compliance event to


* **Return type**

    `Optional`[`int`]



#### create_resource_type(resource_type)
Create a resource type


* **Return type**

    `ResourceType`



#### create_service(service)
Create a new service


* **Return type**

    `Service`



#### create_system(name, stage)
Create a new system


* **Return type**

    `Environment`



#### create_technical_control(technical_control)

* **Return type**

    `TechnicalControl`



#### get_application_environment_by_reference(reference)
Look up an application by the provided reference


* **Return type**

    Application | None



#### get_control(control)

* **Return type**

    `Optional`[`Control`]



#### get_environments()
Get a list of environments


#### get_exclusion_resources(state)
Get a list of exclusion resources by state


#### get_framework(framework)

* **Return type**

    `Optional`[`Framework`]



#### get_framework_control_objective(framework_control_objective)

* **Return type**

    `Optional`[`FrameworkControlObjective`]



#### get_framework_control_objective_link(framework_control_objective, control)

* **Return type**

    `Optional`[`FrameworkControlObjectiveLink`]



#### get_framework_section(framework_section)

* **Return type**

    `Optional`[`FrameworkSection`]



#### get_resource_id(reference, application_environment_id)
Get the id of a resource by its application id and reference


* **Return type**

    `Optional`[`int`]



#### get_resource_type(reference)
Get the id of a resource by its application id and reference


* **Return type**

    `Optional`[`ResourceType`]



#### get_services()
Get a list of services


#### get_system_id_by_name(name)

#### get_technical_control(reference)
Get a Technical Control by its reference


* **Return type**

    `TechnicalControl`



#### get_url(route)
Helper method to resolve route to full url


* **Return type**

    `str`



#### save_monitored_resource(technical_control_id, resource_id, state)
Persist the current status of a montiored resource


* **Return type**

    `None`



#### save_resource(resource)
Create a barebone resource for linking compliance event to


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



#### handle_compliance_event(compliance_event)
When passed a compliance event this method will attempt to create any missing defintions for Application and Technical Controls and persist the presented event


* **Return type**

    `None`



#### handle_control(control)

* **Return type**

    `Control`



#### handle_framework_control_objective(framework_control_objective)

* **Return type**

    `FrameworkControlObjective`



#### handle_framework_control_objective_link(framework_control_objective, control)

* **Return type**

    `FrameworkControlObjectiveLink`



#### handle_resource(resource)

* **Return type**

    `None`



#### handle_resource_type(resource_type)

* **Return type**

    `ResourceType`



#### handle_technical_control(technical_control)
When passed a technical control this method will check its existance and if it does not exist a new one will be created. The technical control is returned


* **Return type**

    `TechnicalControl`



#### set_exclusion_resource_state(id, state)
Set the status of a exclusion resource


* **Parameters**

    
    * **id** (`int`) – The id of the exclusion resource to update


    * **state** (`ExclusionResourceState`) – The state to set the excusion to



* **Return type**

    `None`



### client.airviewclient.client.get_aws_cognito_token(client_id, client_secret, cognito_pool_domain_prefix, aws_region, scope='airview/agent_push')
Helper method to get an AWS Cognito token for use with the client
:type client_id: `str`
:param client_id: Cognito Client ID
:type client_secret: `str`
:param client_secret: Cognito Client Secret
:type cognito_pool_domain_prefix: `str`
:param cognito_pool_domain_prefix: Cognito User Pool Domain Name Prefix
:type aws_region: `str`
:param aws_region: AWS Region Name
:type scope: `str`
:param scope: OAuth Scope
:rtype: `str`
:return: HTTP Authorization header value


### client.airviewclient.client.get_azure_token(client_id, client_secret, tenant_id, scope)
Helper method to get an Azure AD token for use with the client
:type client_id: `str`
:param client_id: Client ID
:type client_secret: `str`
:param client_secret: Client Secret
:type tenant_id: `str`
:param tenant_id: Azure Tenant ID
:type scope: `str`
:param scope: OAuth Scope
:rtype: `str`
:return:


### client.airviewclient.client.get_handler(base_url, system_name, system_stage, referencing_type, token)
Get an instance of handler using the configuration provided


* **Parameters**

    
    * **base_url** (`str`) – The base url at which the AirView API is located


    * **system_name** (`str`) – The unique name which identifies this system


    * **referencing_type** (`str`) – The common reference type which will be used to identify/deduplicate applications e.g. aws_account_id


    * **token** (`str`) – The access token to be used to authenticate with the API



* **Return type**

    `Handler`



### client.airviewclient.client.get_oauth_token(oauth_endpoint, client_id, client_secret, scope, additional_headers=None)
Helper method to get OAuth Token
:type oauth_endpoint: `str`
:param oauth_endpoint: OAuth Token endpoint
:type client_id: `str`
:param client_id: Client ID
:type client_secret: `str`
:param client_secret: Client Secret
:type scope: `str`
:param scope: OAuth Scope(s)
:type additional_headers: 
:param additional_headers: Addtional HTTP Request Headers
:rtype: `str`
:return: HTTP Authorization header value

## client.airviewclient.models module


### _class_ client.airviewclient.models.Application(name, reference, type=ApplicationType.BUSINESS_APPLICATION, environment=Environment(name='Unknown', abbreviation='UNK', id=None), id=None, application_environment_id=None)
Bases: `object`

Dataclass representing application definition


#### \__init__(name, reference, type=ApplicationType.BUSINESS_APPLICATION, environment=Environment(name='Unknown', abbreviation='UNK', id=None), id=None, application_environment_id=None)

#### application_environment_id(_: `Optional`[`int`_ _ = Non_ )
Internal id of application environment


#### environment(_: `Environment_ _ = Environment(name='Unknown', abbreviation='UNK', id=None_ )
Defintion of environment which the application sits in


#### id(_: `Optional`[`int`_ _ = Non_ )
Internal identifier of application


#### name(_: `str_ )
Name of application


#### reference(_: `str_ )
Unique reference of application within the system. e.g. aws account id, azure subscription id


#### type(_: `ApplicationType_ _ = _ )
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

#### base_url(_: `str_ )
Base url of the AirView api


#### referencing_type(_: `str_ )
Type of reference which will be used when identifying an application. e.g. aws_account_id


#### system_name(_: `str_ )
Unique name which identifies this system


#### system_stage(_: `SystemStage_ )
Stage at which this instance monitors


#### token(_: `str_ )
Access token to be used when interacting with the backend


### _exception_ client.airviewclient.models.BackendFailureException()
Bases: `Exception`


### _class_ client.airviewclient.models.ComplianceEvent(resource_reference, application, technical_control, status, additional_data='')
Bases: `object`

Dataclass representing an incoming compliance event


#### \__init__(resource_reference, application, technical_control, status, additional_data='')

#### additional_data(_: `str_ _ = '_ )
Any additional textual data to associate with the event


#### application(_: `Application_ )
Application within which the resource sits


#### resource_reference(_: `str_ )
Unique reference of the resource within the connecting system


#### status(_: `MonitoredResourceState_ )
The enum status of the event


#### technical_control(_: `TechnicalControl_ )
Technical control which this compliance event is the subject of


### _class_ client.airviewclient.models.Control(name, quality_model=None, service_id=None, service_name=None, id=None, severity=ControlSeverity.LOW)
Bases: `object`


#### \__init__(name, quality_model=None, service_id=None, service_name=None, id=None, severity=ControlSeverity.LOW)

#### id(_: `Optional`[`int`_ _ = Non_ )
Id of the framework control objective


#### name(_: `str_ )
Name of the control


#### quality_model(_: `QualityModel_ _ = Non_ )
Quality model of the control


#### service_id(_: `Optional`[`int`_ _ = Non_ )
Service id this control links to


#### service_name(_: `Optional`[`str`_ _ = Non_ )
Name of the service this control is linked to


#### severity(_: `Optional`[`ControlSeverity`_ _ = _ )
severity


### _class_ client.airviewclient.models.ControlSeverity(value)
Bases: `Enum`

An enumeration.


#### CRITICAL(_ = _ )

#### HIGH(_ = _ )

#### LOW(_ = _ )

#### MEDIUM(_ = _ )

### _class_ client.airviewclient.models.Environment(name, abbreviation, id=None)
Bases: `object`

Dataclass representing environment


#### \__init__(name, abbreviation, id=None)

#### abbreviation(_: `str_ )
Abbreviated name of the environment


#### id(_: `Optional`[`int`_ _ = Non_ )
internal id for the environment


#### name(_: `str_ )
Name of environment


### _class_ client.airviewclient.models.ExclusionResource(id, reference, technical_control_reference, application_reference, state)
Bases: `object`

Dataclass representing an exclusion resource


#### \__init__(id, reference, technical_control_reference, application_reference, state)

#### application_reference(_: `str_ )
unique reference for the application


#### id(_: `int_ )
Internal id of the exclusion resource


#### reference(_: `str_ )
Reference of the exclusion resource


#### state(_: `ExclusionResourceState_ )
status of the exclusion resource


#### technical_control_reference(_: `str_ )
unique reference for the technical control


### _class_ client.airviewclient.models.ExclusionResourceState(value)
Bases: `Enum`

An enumeration.


#### ACTIVE(_ = _ )

#### NONE(_ = _ )

#### PENDING(_ = _ )

### _class_ client.airviewclient.models.Framework(name, link, id=None)
Bases: `object`


#### \__init__(name, link, id=None)

#### id(_: `Optional`[`int`_ _ = Non_ )
Id of the framework


#### link(_: `str_ )
Link to the framework


#### name(_: `str_ )
Name of the framework


### _class_ client.airviewclient.models.FrameworkControlObjective(name, link, framework_section, id=None)
Bases: `object`


#### \__init__(name, link, framework_section, id=None)

#### framework_section(_: `FrameworkSection_ )

#### id(_: `Optional`[`int`_ _ = Non_ )
Id of the framework control objective


#### link(_: `str_ )
Link to the control objective in the framework


#### name(_: `str_ )
Name of the control objective


### _class_ client.airviewclient.models.FrameworkControlObjectiveLink(framework_control_objective_id, control_id, id=None)
Bases: `object`


#### \__init__(framework_control_objective_id, control_id, id=None)

#### control_id(_: `int_ )
Id of the control


#### framework_control_objective_id(_: `int_ )
Id of the control objective


#### id(_: `Optional`[`int`_ _ = Non_ )
Id of the framework control objective


### _class_ client.airviewclient.models.FrameworkSection(name, link, framework, id=None)
Bases: `object`


#### \__init__(name, link, framework, id=None)

#### framework(_: `Framework_ )
Framework within which the section belongs


#### id(_: `Optional`[`int`_ _ = Non_ )
Id of the framework section


#### link(_: `str_ )
Link to the section framework (domain)


#### name(_: `str_ )
Name of the section in the framework


### _class_ client.airviewclient.models.MonitoredResourceState(value)
Bases: `Enum`

An enumeration.


#### DELETED(_ = _ )

#### FLAGGED(_ = _ )

#### MONITORING(_ = _ )

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

### _class_ client.airviewclient.models.Resource(reference, application, name=None, resource_type=None)
Bases: `object`

Dataclass representing an resource


#### \__init__(reference, application, name=None, resource_type=None)

#### application(_: `Application_ )
Application within which the resource sits


#### name(_: `Optional`[`str`_ _ = Non_ )
A friendly name for the resource


#### reference(_: `str_ )
Unique reference of the resource within the connecting system


#### resource_type(_: `Optional`[`ResourceType`_ _ = Non_ )
The resource type which this resource belongs to


### _class_ client.airviewclient.models.ResourceType(reference, name, id=None, service=None)
Bases: `object`

Dataclass representing a resource type


#### \__init__(reference, name, id=None, service=None)

#### id(_: `Optional`[`int`_ _ = Non_ )
Internal identifier of resource type


#### name(_: `str_ )
A friendly name for the resource type


#### reference(_: `str_ )
Unique reference of the resouce type


#### service(_: `Optional`[`Service`_ _ = Non_ )
The service which this resource belongs to


### _class_ client.airviewclient.models.Service(reference, name, type, id=None)
Bases: `object`

Dataclass representing a service


#### \__init__(reference, name, type, id=None)

#### id(_: `Optional`[`int`_ _ = Non_ )
Internal identifier of service


#### name(_: `str_ )
A friendly name for the service


#### reference(_: `str_ )
Unique reference of the service within the connecting system


#### type(_: `ServiceType_ )
The type of service this is


### _class_ client.airviewclient.models.ServiceType(value)
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

#### UNKNOWN(_ = _ )

#### VIRTUAL_MACHINE(_ = _ )

### _class_ client.airviewclient.models.SystemStage(value)
Bases: `Enum`

An enumeration.


#### BUILD(_ = _ )

#### MONITOR(_ = _ )

### _class_ client.airviewclient.models.TechnicalControl(name, reference, control_action, id=None, ttl=None, is_blocking=None, control_id=None, control=None)
Bases: `object`

Dataclass representing technical control definition


#### \__init__(name, reference, control_action, id=None, ttl=None, is_blocking=None, control_id=None, control=None)

#### control(_: `Optional`[`Control`_ _ = Non_ )
Parent control


#### control_action(_: `TechnicalControlAction_ )
Type of control


#### control_id(_: `Optional`[`int`_ _ = Non_ )
Id of parent control


#### id(_: `Optional`[`int`_ _ = Non_ )
Id of control


#### is_blocking(_: `Optional`[`bool`_ _ = Non_ )
Should a failure cause a process to exit


#### name(_: `str_ )
The name of the technical control


#### reference(_: `str_ )
Unique reference for the control within the connecting system


#### ttl(_: `Optional`[`int`_ _ = Non_ )
ttl of the technical control


### _class_ client.airviewclient.models.TechnicalControlAction(value)
Bases: `Enum`

An enumeration.


#### INCIDENT(_ = _ )

#### LOG(_ = _ )

#### TASK(_ = _ )

#### VULNERABILITY(_ = _ )
## Module contents
