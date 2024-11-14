# syntax=docker/dockerfile:1

# Use the official Python 3.11.2 image as base
FROM python:3.11.2

# Set the working directory within the container
WORKDIR /abrechnungsformular

# Upgrade pip and install Python dependencies
COPY ./requirements.txt /abrechnungsformular/requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

# Setup non-root user to run the app (security best practice)
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" --no-create-home --uid "${UID}" appuser
USER appuser

# Copy the necessary files and directories into the container
COPY . /abrechnungsformular

# Define the command to run the Flask application
CMD ["python3", "abrechnungsformular.py"]
