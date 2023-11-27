#!/bin/sh

set -ex

cd /opt/src/db && alembic upgrade head

cd /opt/src &&  gunicorn main:app --bind 0.0.0.0:8080 -w 4 -k uvicorn.workers.UvicornWorker
