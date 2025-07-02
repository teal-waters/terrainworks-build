#!/bin/bash

# TODO: make these variables command arguments
APP_VERSION="0.1"
APP_NAME="bldgrds"

docker build -t ${APP_NAME}:${APP_VERSION} .
docker volume create ${APP_NAME}-${APP_VERSION}-data

docker run -d \
  --name ${APP_NAME}-${APP_VERSION} \
  -v ${APP_NAME}-${APP_VERSION}-data:/data \
  ${APP_NAME}:${APP_VERSION}

docker image ls ${APP_NAME}

docker ps --filter "name=${APP_NAME}-${APP_VERSION}"