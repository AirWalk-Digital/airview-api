from dotenv import dotenv_values
config = dotenv_values(".env")

from airviewclient import client, models
token = client.get_azure_token(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    tenant_id=config["tenant_id"],
    scope=config["scope"],
)
client_handler = client.get_handler(
	base_url=base_url,
	system_id=system_id,
	referencing_type="pipeline_id",
	token=token,
)
environment = models.Environment(name="My Envirionment", abbreviation="env")
application = models.Application(
    name="Test App One", reference="local-identifier", environment=environment
)
client_handler.handle_application(transformed)


