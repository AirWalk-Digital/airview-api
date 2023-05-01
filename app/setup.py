from setuptools import setup, find_packages

setup(
    name="airview_api",
    version="0.0.0",
    description="API for AirView Product",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.2",
        "Flask-SQLAlchemy==2.4.4",
        "psycopg2-binary==2.8.6",
        "sqlalchemy<1.4",
        "flask-smorest==0.31.0",
        "elasticsearch==7.13.0",
        "Werkzeug==2.0.2"
    ],
)
