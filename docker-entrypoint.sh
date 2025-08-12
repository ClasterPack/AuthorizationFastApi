#!/bin/sh

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."
  sleep 2
done
alembic upgrade head

exec "$@"