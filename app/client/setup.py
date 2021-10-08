from setuptools import setup, find_packages

setup(
    name="airviewclient",
    version="0.0.0",
    description="API for AirView Product",
    packages=find_packages(),
    install_requires=["requests==2.25.1"],
)
