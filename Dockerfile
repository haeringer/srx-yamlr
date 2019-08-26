FROM python:3.7-slim

# Project files and settings
LABEL Name=srx-yamlr
ENV PYTHONUNBUFFERED 1
ARG PROJECT_NAME=srx-yamlr
ARG PROJECT_DIR=/opt/srx-yamlr
ARG STATIC_DIR=/var/www/srx-yamlr/static

# Install Python and package Libraries
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y vim git

# Create project directories and copy project files
RUN mkdir -p $PROJECT_DIR $STATIC_DIR
ADD . $PROJECT_DIR
WORKDIR $PROJECT_DIR/django

# Install project dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# Run container as non-root
RUN useradd --create-home --shell /bin/bash srx-yamlr
RUN chown -R srx-yamlr:srx-yamlr $PROJECT_DIR $STATIC_DIR
USER srx-yamlr
