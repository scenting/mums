#!/bin/sh
set -e

# wait for db container
while ! nc -z db 5432; do sleep 3; done

# wait for redis container
while ! nc -z redis 6379; do sleep 3; done

exec "$@"
