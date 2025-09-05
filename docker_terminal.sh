#!/bin/bash

APP_NAME="$1"
APP_VERSION="$2"

if [ -z "$APP_NAME" ] || [ -z "$APP_VERSION" ]; then
    echo "Usage: $0 <app_name> <app_version>"
    exit 1
fi

docker exec -it ${APP_NAME}-${APP_VERSION} /bin/bash
