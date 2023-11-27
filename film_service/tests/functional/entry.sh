#!/usr/bin/env bash

set -e

python3 /app/tests/functional/utils/wait_for_es.py
python3 /app/tests/functional/utils/wait_for_redis.py

pytest . -vvv