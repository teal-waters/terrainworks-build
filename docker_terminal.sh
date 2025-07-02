#!/bin/bash

# TODO: make these variables command arguments
APP_VERSION="0.1"
APP_NAME="bldgrds"

docker exec -it ${APP_NAME}-${APP_VERSION} /bin/bash
