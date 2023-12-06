#!/bin/sh

set -ex

cd /opt/src/db && alembic upgrade head

cd /opt/src && $1
