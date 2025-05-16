#!/usr/bin/env bash
# exit on error
set -o errexit

# Install essential dependencies only
pip install django==5.2.1 django-cors-headers==4.3.1 djangorestframework==3.15.0 gunicorn==21.2.0 whitenoise==6.6.0

# Generate static files directory (without collecting)
mkdir -p staticfiles
