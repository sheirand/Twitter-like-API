#!/bin/sh

set -e

echo "Celery worker starting..."

celery -A core worker -l info --loglevel=INFO

exec "$@"