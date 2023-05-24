from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException

# from airview_api.models import ApplicationTechnicalControl
from airview_api.database import db


def get_by_ids(application_id: int, technical_control_id: int):
    app = ApplicationTechnicalControl.query.filter_by(
        application_id=application_id, technical_control_id=technical_control_id
    ).first()
    return app


def create_with_ids(application_id: int, technical_control_id: int):
    try:
        atc = ApplicationTechnicalControl(
            application_id=application_id, technical_control_id=technical_control_id
        )
        db.session.add(atc)
        db.session.commit()
        return atc
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException()
