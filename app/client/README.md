# Reusable python client library for wrapping REST API

This library wraps the required low level API calls to simplify the loading of data into AirView.

## Authentications
The client uses access tokens in the http authorization header to authenticate itself at the api. A suitable token must be obtained prior to handling any incoming events.

### Azure
A convenience method is provided to


### client
#### get_azure_token
#### get_handler

### Handler
#### handle_application
#### handle_compliance_event

## Install

```sh
pip install --ignore-pipfile git+ssh://git@github.com/AirWalk-Digital/airview-api.git#subdirectory=app/client
```



## API Push Example
Canonical example https://github.com/AirWalk-Digital/terraform-aws-airview-ccf/blob/main/lambda_code/airview_api_push/airview_api_push.py#L22

```python
from airviewclient import client, models

# You'll need a client_id, client_secret, and tenant_id

token = client.get_azure_token(
    client_id=client_id,
    client_secret=client_secret,
    tenant_id=tenant_id,
    scope=scope,
)

client_handler = client.get_handler(
    base_url=base_url,
    system_name=system_name,
    system_stage=models.SystemStage.BUILD,
    referencing_type=referencing_type,
    token=token,
)

transformed = models.ComplianceEvent(...)
client_handler.handle_compliance_event(transformed)
```
