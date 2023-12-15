#!/bin/sh




echo "Waiting for PG..."


while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 10
done

echo "PG started"

echo "PROFILE_PG_HOST $PROFILE_PG_HOST"
echo "PROFILE_PG_PORT $PROFILE_PG_PORT"

echo "Waiting for PG Profile..."
while ! nc -z $PROFILE_PG_HOST $PROFILE_PG_PORT; do
  sleep 10
done

echo "Profile started"


python main.py
