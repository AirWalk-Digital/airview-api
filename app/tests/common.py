from airview_api import app
from airview_api.database import db
import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
import testing.postgresql
import os

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)
# sqlite disables fk constraints by default, this enables them
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


@pytest.fixture(scope="function")
def client():
    if os.environ.get("USE_SQLITE") == "True":
        app.DB_URI = "sqlite://"

    else:
        postgresql = Postgresql()
        app.DB_URI = postgresql.url()

    instance = app.create_app()
    ctx = instance.app_context()
    ctx.push()

    db.create_all()
    yield instance.test_client()

    ctx.pop()

@pytest.fixture(scope="function")
def instance():
    app.DB_URI = "sqlite://"
    inst = app.create_app()
    ctx = inst.app_context()
    ctx.push()
    db.create_all()

    yield inst

    ctx.pop()
