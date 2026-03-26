#!/usr/bin/env bash
set -e

export DJANGO_SETTINGS_MODULE=my_cms_project.settings.production
export SECRET_KEY=${SECRET_KEY:-vercel-build-only-dummy-key}

pip install -r requirements-production.txt

python manage.py collectstatic --noinput --clear
