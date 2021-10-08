from airview_api.models import Environment
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.database import db


def get_all():
    return Environment.query.all()

def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app = Environment(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException("Integrity Error, check reference fields")
    return app
