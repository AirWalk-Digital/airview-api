from airview_api.models import *
from airview_api import app


def load():
    print("Loading Base Data")
    instance = app.create_app()
    ctx = instance.app_context()
    ctx.push()

    db.create_all(app=instance)

    if ApplicationType.query.get(1) is None:
        db.session.add(ApplicationType(id=1, name="Business Application"))
    if ApplicationType.query.get(2) is None:
        db.session.add(ApplicationType(id=2, name="Technical Service"))
    if ApplicationType.query.get(3) is None:
        db.session.add(ApplicationType(id=3, name="Application Service"))

    # Environments
    if Environment.query.get(1) is None:
        db.session.add(Environment(id=1, name="Development", abbreviation="Dev"))
    if Environment.query.get(2) is None:
        db.session.add(Environment(id=2, name="Production", abbreviation="Prd"))

    # Systems
    if System.query.get(1) is None:
        db.session.add(System(id=1, name="AWS"))
    if System.query.get(2) is None:
        db.session.add(System(id=2, name="Azure"))

    db.session.commit()
    ctx.pop()


if __name__ == "__main__":
    load()
