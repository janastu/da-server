#! /usr/bin/python2
from flask import Flask

__all__ = ['create_app']

DEFAULT_APP_NAME = __name__


def create_app(app_name=DEFAULT_APP_NAME):
    app = Flask(app_name)
    app.config.from_pyfile('config.py')
    return app
