#!/bin/bash

export DOCKER_BUILDKIT=1
docker-compose rm -stop --volumes social-network-backend-test-db social-network-backend-tests
docker compose up --build tests