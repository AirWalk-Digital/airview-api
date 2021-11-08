from airview_api.models import ApplicationType
from airview_api.database import db
from airview_api.services import AirViewValidationException, AirViewNotFoundException


def get_all():
    return ApplicationType.query.all()

def create(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app_type = ApplicationType(**data)
    db.session.add(app_type)
    db.session.commit()
    return app_type

