# syntax=docker/dockerfile:1

# Use the official Python 3.13.0-slim image as base
FROM python:3.13.0-slim AS base

# Description of resulting image
LABEL org.opencontainers.image.description="Ein Webserver, über welchen Aktive und Helfer des ADFC Hamburg Abrechnungsformulare ausfüllen und herunterladen können."

# Set the working directory within the container
WORKDIR /abrechnungsformular

# Install necessary packages
RUN apt-get update
RUN apt-get install -y fonts-croscore fonts-dejavu-core libpango1.0-0

# Cleanup cache and temporary files from apt-get
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY ./requirements.txt /abrechnungsformular/requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

# Enable writing font cache files (stops fontconfig from throwing errors)
RUN chmod a+w /var/cache/fontconfig/

# Setup non-root user to run the app (security best practice)
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/usr/sbin/nologin" --no-create-home --uid "${UID}" appuser
USER appuser

# Copy the necessary files and directories into the container
COPY app/ /abrechnungsformular/app/
COPY static/ /abrechnungsformular/static/
COPY templates/ /abrechnungsformular/templates/
COPY abrechnungsformular.py VERSION CONTACT.json /abrechnungsformular/

# Expose port 8000 for the Flask application
EXPOSE 8000

# Define the command to run the Flask application using Gunicorn
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "abrechnungsformular:flaskapp"]
