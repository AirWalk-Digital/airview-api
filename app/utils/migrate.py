# import sys
# sys.path.insert(1, '../airview-api')
from airview_api.app import create_app
from flask_migrate import Migrate

app = create_app()

from airview_api.database import db

migrate = Migrate(app, db)
