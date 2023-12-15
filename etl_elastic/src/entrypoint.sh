#!/bin/sh




echo "Waiting for PG..."


while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 10
done

echo "PG started"

echo "Waiting for Elastic..."


while ! nc -z $ELASTIC_HOST $ELASTIC_PORT; do
  sleep 10
done

echo "Elastic started"



python main.py

exec "$@"
