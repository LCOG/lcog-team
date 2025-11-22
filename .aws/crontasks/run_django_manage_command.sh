#!/usr/bin/env bash

# Check that exactly one argument was supplied to the script.
# Exit if there are more or fewer arguments.
if [[ $# -ne 1 ]]; then
  echo "run_django_manage_command expected 1 argument; got $# arguments instead:" "$@"
  echo "Usage: run_django_manage_command <command>"
  exit 1
fi

# The command we pass to manage.py is the argument given to the script
COMMAND=$1

# On the EC2 host, the container names follow the pattern
# "ecs-<task definition family>-<task definition revision>-<container name in task definition>-<ECS ID string>"
# Get the Docker ID for the API container by filtering active containers by the
# name assigned to the container in the task definition.
API_CONTAINER_ID=$(docker ps --filter "name=django-api" --format "{{.ID}}")

# Check that a container ID was retrieved.
# If not, print out the Docker containers that are running and exit.
if [[ -z $API_CONTAINER_ID ]]; then
  echo -e "Could not find API container ID. Currently running containers:\n$(docker ps)"
  exit 1
fi


# Run the provided manage.py command in the Django container
echo "Running command $COMMAND in container $API_CONTAINER_ID..."
docker exec "$API_CONTAINER_ID" python3 manage.py "$COMMAND"