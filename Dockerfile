FROM python:3.8

RUN python -m venv /venv && \
    . /venv/bin/activate && \
    mkdir /app && \
    cd /app && \
    git clone https://github.com/AirWalk-Digital/airview-api.git . && \
    cd app && \
    pip install -r requirements.txt

WORKDIR /app/app
CMD sleep 3 && . /venv/bin/activate && FLASK_APP=./utils/debug.py FLASK_DEBUG=True LOAD_DATA=True DATABASE_URI=$DB_CONN_STR CREATE_DB=True FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=80 flask run