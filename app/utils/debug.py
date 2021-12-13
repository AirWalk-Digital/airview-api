import os
from pprint import pprint
from airview_api import app
from airview_api.database import db
from airview_api.models import ApplicationType, Environment, System

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

# sqlite disables fk constraints by default, this enables them
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


# if os.environ.get("CREATE_DB", "") == "True":
# from data_loader import load_all

# load_all.load()

instance = app.create_app()


if __name__ == "__main__":
    instance.run(debug=True)
