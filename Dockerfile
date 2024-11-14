# syntax=docker/dockerfile:1

# Use the official Python 3.11.2 image as base
FROM python:3.11.2

# Set the working directory within the container
WORKDIR /abrechnungsformular

# Install Python dependencies
COPY ./requirements.txt /abrechnungsformular/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

# Copy the necessary files and directories into the container
COPY . /abrechnungsformular

# Define the command to run the Flask application
CMD ["python3", "abrechnungsformular.py"]
