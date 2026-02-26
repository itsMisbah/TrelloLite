#!/usr/bin/env bash

echo "Starting Gunicorn server..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT