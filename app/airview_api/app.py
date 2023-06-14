import os
from flask import Flask
from flask_smorest import Api
from airview_api import database
from airview_api import controllers


DB_URI = os.environ.get("DATABASE_URI")


def create_app(app=None, db_connection_string=None):
    """
    Create Airview API Flask App
    :param app: Pre-existing "flask-like" app object
    :param db_connection_string: Database connection string
    :return: Flask App
    """
    if not app:
        app = Flask(__name__)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        db_connection_string if db_connection_string else DB_URI
    )

    database.init_app(app)

    app.config["API_TITLE"] = "AirView API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"

    api = Api(app)
    api.register_blueprint(controllers.applications.blp)
    api.register_blueprint(controllers.application_environments.blp)
    api.register_blueprint(controllers.resources.blp)
    api.register_blueprint(controllers.technical_controls.blp)
    api.register_blueprint(controllers.systems.blp)
    api.register_blueprint(controllers.services.blp)
    api.register_blueprint(controllers.environments.blp)
    api.register_blueprint(controllers.compliance.blp)
    # api.register_blueprint(controllers.control_statuses.blp)
    # api.register_blueprint(controllers.application_statuses.blp)
    # api.register_blueprint(controllers.exclusion_resources.blp)
    api.register_blueprint(controllers.referenced_application_environments.blp)
    # api.register_blueprint(controllers.application_technical_controls.blp)
    api.register_blueprint(controllers.monitored_resources.blp)
    #    api.register_blueprint(controllers.exclusions.blp) # This is commented cos moving resources to own table broke it and it needs a rethink
    #    api.register_blueprint(controllers.search.blp)

    return app
