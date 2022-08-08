from airview_api.app import create_app
from flask_aws_http_apigw import FlaskLambdaHttp
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection


lambda_api_http = FlaskLambdaHttp(__name__)
handler = create_app(lambda_api_http)


# sqlite disables fk constraints by default, this enables them
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


if __name__ == '__main__':
    handler.run(debug=False)
