# Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
FROM python:3.12-slim-bookworm

# Add user that will be used in the container.
RUN useradd wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE" command.
# 3. Set Django settings module to production.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=my_cms_project.settings.production

# Install system packages required by Wagtail, Django, and media processing.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    ffmpeg \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# Install the application server.
RUN pip install "gunicorn==20.0.4"

# Install the project requirements.
COPY requirements-production.txt /
RUN pip install -r /requirements-production.txt

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user.
RUN chown wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

# Collect static files (use a dummy SECRET_KEY only for this build step).
RUN SECRET_KEY=collectstatic-build-only python manage.py collectstatic --noinput --clear

# Runtime command: migrate then start gunicorn.
CMD set -xe; python manage.py migrate --noinput; gunicorn my_cms_project.wsgi:application
