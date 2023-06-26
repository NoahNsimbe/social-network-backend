#!/bin/bash

read -p "Enter your absract API key: " ABSTRACT_API_KEY

CONTENT="
SECRET_KEY=%2m&(_bkr%j01wmgl(08r#qbmxsks#d75nrb&glt
RDS_DB_NAME=social_network_tools_db
RDS_USERNAME=admin
RDS_PASSWORD=admin
RDS_HOSTNAME=db
POSTGRES_DB=social_network_tools_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
RDS_PORT=5432
ABSTRACT_API_KEY=$ABSTRACT_API_KEY
CELERY_BROKER_URL=redis://redis
"
ENV_FILE=".env"

echo "$CONTENT" > $ENV_FILE

echo ".env file created successfully at '$(pwd)/$ENV_FILE'."

exit 0
