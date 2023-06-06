# Overview
This how to guide outlines the steps required to record compliance related information in AirView using the client library.

# Terminology
**Application:** The top level definition of an application against which compliance events can be recorded.

**Environment:** The environment in which an application sits. e.g. development, production, UAT.

**Compliance Event:** An update to the status of technical control against an application.

**Technical Control:** Definition of a specific mechanism which can used to protect an application.

**Exclusion:** A logical grouping of exclusion resources which were requested at the same time

**Exclusion Resource:** An active exclusion resource will prevent AirView surfacing non compliant events for the targeted technical control and application.


# Installation
The client can be installed via pip referencing the github url of the library. e.g.

```
pip install git+ssh://git@github.com/AirWalk-Digital/airview-api.git@main#subdirectory=app/client
```

# Authentication
Before interacting with the client a suitable access token must be obtained from the authentication provider.
## Microsoft Azure
A helper method is provided for convenience:

```
    token = client.get_azure_token(
        client_id="my_client_id",
        client_secret="my_secret",
        tenant_id="my_tenant",
        scope="my_scope",
    )
```
## Custom
For any other authentication provider it is necessary to first obtain a JWT which can be then used to interact with the AirView client. This will depend on the specific platform to which AirView has been deployed.

# Creating a handler
Interaction with the client primarily happens via the [Handler](./airviewclient.md#class-clientairviewclientclienthandlerbackend) class. The method [get_handler](./airviewclient.md#clientairviewclientclientget_handlerbase_url-system_id-referencing_type-token) returns an instance of the class based on the configuration provided in the parameters.

```
client_handler = client.get_handler(
	base_url=base_url,
	system_id=system_id,
	referencing_type=referencing_type,
	token=token,
)

```

# Persisting an application
The method [handle_application](./airviewclient.md#clientairviewclientclientget_handlerbase_url-system_id-referencing_type-token) expects an [Application](./airviewclient.md#class-clientairviewclientmodelsapplicationname-reference-environmentnone-type1-idnone-parent_idnone) to be passed as an argument. When called, the AirView client will attempt to create or update the definition within AirView.

```
environment = models.Environment(name="My Envirionment", abbreviation="env")
application = models.Application(
    name="Test App One", reference="local-identifier", environment=environment
)
client_handler.handle_application(transformed)

```

# Persisting a compliance event
A compliance event can be sent to AirView via the method. [handle_compliance_event](./airviewclient.md#handle_compliance_eventcompliance_event)

The method expects a [ComplianceEvent](./airviewclient.md#class-clientairviewclientmodelscomplianceeventresource_reference-application-technical_control-status) to be passed in as a parameter.

The method will attempt to create a basic representation of the provided application if it does not exist.

The method will attempt to create the definition of the technical control if it does not exist.

```

application = models.Application(name="Test App One", reference="local-app-identifier")
technical_control = models.TechnicalControl(
    name="All servers should be patched",
    reference="local_control_identifier",
    control_action=TechnicalControlAction.VULNERABILITY,
)
compliance_event = models.ComplianceEvent(
	application=application,
	technical_control=technical_control,
	resource_reference=resource_ref,
	status=MonitoredResourceState.FLAGGED,
)

client_handler.handle_compliance_event(transformed)

```
# Handling Exclusions
Exclusions are created via the frontend user interface and begin in a status of pending. Non compliance will continue to be surfaced until the exclusion is marked as active. 2 methods are provided to manage the activation of pending exclusions. The client does not support any status change other than the activation of pending exclusions.

## Get list of pending exclusions
The method [get_exclusions_by_state](./create-guide./airviewclient.md#get_exclusions_by_statestate)
expects an [ExclusionState] as a parameter and will return an array of all exclusions of matching state. The results are scoped to the system_id for which the client was created. This allows each system to manage it's own exclusion approval logic.

```
client.get_exclusions_by_state(models.ExclusionResourceState.PENDING)
```

## Set exclusion state

The method [set_exclusion_resource_state](./airviewclient.md#set_exclusion_resource_stateid-state) sets the state of exclusion with the matching id


```
client.set_exclusion_resource_state(
	id=123, state=models.ExclusionResourceState.ACTIVE
)

```
