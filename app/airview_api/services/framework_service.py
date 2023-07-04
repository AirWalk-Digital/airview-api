from airview_api.models import (
    Framework,
    FrameworkSection,
    FrameworkControlObjective,
    FrameworkControlObjectiveLink
)
from sqlalchemy.exc import IntegrityError
from airview_api.services import AirViewValidationException, AirViewNotFoundException
from airview_api.database import db




def create_framework(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    
    app = Framework(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return app


def create_framework_section(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    app = FrameworkSection(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return app


def create_control_objective(data: dict):
    if data.get("id") is not None:
        raise AirViewValidationException("Id is not expected when creating record")
    
    app = FrameworkControlObjective(**data)
    try:
        db.session.add(app)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise AirViewValidationException(
            "Unique Constraint Error, check reference field"
        )
    return app


def get_all():
    return Framework.query.all()


def get_by_id(framework_id: int):
    return Framework.query.get(framework_id)


def get_sections_by_framework(framework_id: int):
    return FrameworkSection.query.filter_by(framework_id=framework_id)


def get_controls_by_framework_and_section(section_id: int):
    return FrameworkControlObjective.query.filter_by(framework_section_id=section_id)


def get_framework_by_name(name: str):
    data = Framework.query.filter_by(name=name).all()
    return data


def get_framework_section_by_name(name: str):
    data = FrameworkSection.query.filter_by(name=name).all()
    return data


def get_control_by_name(name: str):
    data = FrameworkControlObjective.query.filter_by(name=name).all()
    return data


# def create_control_objective_link(data: dict):
#     try:
#         app = FrameworkControlObjectiveLink(**data)
#         db.session.add(app)
#         db.session.commit()
#     except IntegrityError as e:
#         db.session.rollback()
#         raise AirViewValidationException(
#             "Unique Constraint Error, check reference field"
#         )
#     return app


# def get_control_objective_links():
#     return FrameworkControlObjectiveLink.query.all()
