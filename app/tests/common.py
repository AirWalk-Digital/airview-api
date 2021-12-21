from airview_api import app
from airview_api.database import db
import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
import testing.postgresql

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
    postgresql = Postgresql()
    app.DB_URI = postgresql.url()

    # app.DB_URI = "sqlite://"
    instance = app.create_app()
    db.create_all(app=instance)
    ctx = instance.app_context()
    ctx.push()

    yield instance.test_client()

    ctx.pop()


@pytest.fixture(scope="function")
def instance():
    app.DB_URI = "sqlite://"
    inst = app.create_app()
    db.create_all(app=inst)
    ctx = inst.app_context()
    ctx.push()

    yield inst

    ctx.pop()
