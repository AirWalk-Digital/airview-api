from airview_api.app import create_app
from flask_aws_http_apigw import FlaskLambdaHttp
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
import boto3
import json
import os
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(
    dbapi_connection: SQLite3Connection, connection_record: any
) -> None:
    """
    sqlite disables fk constraints by default, this enables them
    :param dbapi_connection:
    :param connection_record:
    """
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def fetch_aws_secrets_db_credentials(secret_arn: str) -> dict:
    """
    Fetch Database credentials from AWS Secrets Manager
    :param secret_arn: AWS Secret ARN
    :return: Secret JSON
    """
    sm = boto3.client("secretsmanager")

    try:
        response = sm.get_secret_value(SecretId=secret_arn)
    except Exception as e:
        logger.error("Failed to fetch secret %s: '%s'", secret_arn, e)
        raise

    try:
        secret_blob = json.loads(response.get("SecretString"))
    except Exception as e:
        logger.error("Failed to parse secret %s: '%s'", secret_arn, e)
        raise

    return secret_blob


def get_db_conn_string() -> str:
    """
    Get Formatted Connection String
    :return: Postgres Connection URL
    """
    try:
        secret_arn: str = os.environ["DB_CREDS_SECRET_NAME"]
    except KeyError:
        logger.error("DB_CREDS_SECRET_NAME' environment variable not set")
        raise

    try:
        database_name: str = os.environ["DB_NAME"]
    except KeyError:
        logger.error("'DB_NAME' environment variable not set")
        raise

    try:
        rds_proxy_endpoint: str = os.environ["DB_PROXY_HOST"]
    except KeyError:
        logger.error("'DB_PROXY_HOST' environment variable not set")
        raise

    credentials: dict = fetch_aws_secrets_db_credentials(secret_arn=secret_arn)
    connection_string: str = "postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".format(
        DB_USERNAME=credentials.get("username"),
        DB_PASSWORD=credentials.get("password"),
        DB_HOST=rds_proxy_endpoint,
        DB_PORT=credentials.get("port"),
        DB_NAME=database_name
    )

    return connection_string


lambda_api_http: FlaskLambdaHttp = FlaskLambdaHttp(__name__)
handler: FlaskLambdaHttp = create_app(
    app=lambda_api_http, db_connection_string=get_db_conn_string()
)


if __name__ == "__main__":
    handler.run(debug=False)
