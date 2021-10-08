BUSINESS = 1  # Business Application
TECH = 2  # Technical Service

# List apps here (name, reference, application_type)

apps = [
    # ("App One", "A1", BUSINESS),
    # ("App Two", "A2", TECH),
    # ("App Three", "A3", BUSINESS),
]

# Ignore after here


from airview_api.models import *
from airview_api import app


def load_app(name, ref, app_type):
    if Application.query.filter_by(name=name).first() is None:
        db.session.add(
            Application(name=name, reference=ref, application_type_id=app_type)
        )


def load():
    print("Loading Applications")
    instance = app.create_app()
    ctx = instance.app_context()
    ctx.push()

    db.create_all(app=instance)
    for a in apps:
        load_app(*a)

    db.session.commit()
    ctx.pop()


if __name__ == "__main__":
    load()
