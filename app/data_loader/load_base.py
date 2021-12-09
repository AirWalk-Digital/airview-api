from airview_api.models import *
from airview_api import app


def load():
    print("Loading Base Data")
    instance = app.create_app()
    ctx = instance.app_context()
    ctx.push()

    db.create_all(app=instance)

    if ApplicationType.query.filter_by(name="Business Application").first() is None:
        db.session.add(ApplicationType(name="Business Application"))
    if ApplicationType.query.filter_by(name="Technical Service").first() is None:
        db.session.add(ApplicationType(name="Technical Service"))
    if ApplicationType.query.filter_by(name="Application Service").first() is None:
        db.session.add(ApplicationType(name="Application Service"))

    # Environments
    if Environment.query.filter_by(abbreviation="DEV").first() is None:
        db.session.add(Environment(name="Development", abbreviation="DEV"))
    if Environment.query.filter_by(abbreviation="PRD").first() is None:
        db.session.add(Environment(name="Production", abbreviation="PRD"))

    # Systems
    if System.query.filter_by(name="AWS").first() is None:
        db.session.add(System(name="AWS", stage=SystemStage.BUILD))
    if System.query.filter_by(name="Azure").first() is None:
        db.session.add(System(name="Azure", stage=SystemStage.BUILD))

    db.session.commit()
    ctx.pop()


if __name__ == "__main__":
    load()
