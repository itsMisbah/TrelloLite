#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser if none exists..."
python manage.py create_superuser_if_none

echo "Creating demo data..."
python manage.py create_demo_data

echo "Build completed successfully!"