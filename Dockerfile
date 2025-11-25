# syntax=docker/dockerfile:1

# Use the official Python Alpine image as base
FROM python:3.13.7-alpine3.22 AS base

# Description of resulting image
LABEL org.opencontainers.image.description="Ein Webserver, über welchen Aktive und Helfer des ADFC Abrechnungsformulare ausfüllen und herunterladen können."

# Set the working directory within the container
WORKDIR /abrechnungsformular

# Install necessary packages, then delete package index and cache
RUN apk update \
 && apk add font-croscore font-dejavu pango \
 && apk cache clean \
 && rm -rf /var/cache/apk/* /lib/apk/db/*

# Upgrade pip and install Python dependencies
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /abrechnungsformular/requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

# Enable writing font cache files (stops fontconfig from throwing errors)
RUN chmod a+w /var/cache/fontconfig/

# Copy the necessary files and directories into the container
COPY app/ /abrechnungsformular/app/
COPY static/ /abrechnungsformular/static/
COPY templates/ /abrechnungsformular/templates/
COPY abrechnungsformular.py CONFIG.ini tool_*.py /abrechnungsformular/

# Generate files via Python scripts
RUN mkdir /abrechnungsformular/static/blank; python /abrechnungsformular/tool_generate_empty_pdf.py -ar /abrechnungsformular/static/blank/; rm /abrechnungsformular/tool_generate_empty_pdf.py
RUN python /abrechnungsformular/tool_generate_white_logos.py -nv /abrechnungsformular/static/img/logo.svg; rm /abrechnungsformular/tool_generate_white_logos.py

# Setup non-root user to run the app (security best practice)
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/usr/sbin/nologin" --no-create-home --uid "${UID}" appuser
USER appuser

# Expose port 8000 for the Flask application
EXPOSE 8000

# Define the command to run the Flask application using Gunicorn
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "abrechnungsformular:flaskapp"]

# Store version number as environment variable
ARG VERSION
ENV DOCKER_IMAGE_VERSION=${VERSION}
