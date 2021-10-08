from airview_api.models import ApplicationType
from airview_api.database import db


def get_all():
    return ApplicationType.query.all()
