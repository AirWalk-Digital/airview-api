#!/usr/bin/env bash
FLASK_APP=./app.py FLASK_DEBUG=True DATABASE_URI=sqlite:// flask run
