#!/usr/bin/env bash
# This script runs at startup on Render

# Run migrations on startup
python manage.py migrate

# If we need to create a temporary uploads directory
mkdir -p media/uploads

# Get the PORT environment variable that Render sets
PORT=${PORT:-8000}

# Start the application with specific host and port
exec gunicorn realestate_project.wsgi:application --bind 0.0.0.0:$PORT
