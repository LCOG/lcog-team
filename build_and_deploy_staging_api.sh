#!/usr/bin/env bash

# Set strict mode
set -eou pipefail

# Set AWS profile for logging in to Docker and pushing the image
AWS_PROFILE=${AWS_PROFILE:?Set the AWS_PROFILE variable to your ECS developer profile: export AWS_PROFILE=<AWS profile name>}
echo "Using AWS profile $AWS_PROFILE"

# URI for the backend API image repository on ECR
REPO_URI="311127195930.dkr.ecr.us-west-2.amazonaws.com/backend/api"

# Get the login password for the ECR and pass it to Docker to allow pushing
# to the ECR repository
echo "Retrieving ECR login password and logging in to Docker..."
aws ecr get-login-password --profile $AWS_PROFILE \
  | docker login --username AWS --password-stdin 311127195930.dkr.ecr.us-west-2.amazonaws.com

# Build and push the container image using Docker CLI
API_VERSION=$(date -I | tr - .)-$(git rev-parse --short HEAD)
echo "Building API image with version $API_VERSION ..."
docker build -t backend/api:$API_VERSION .
echo "Finished building backend/api:$API_VERSION"

echo "Tagging image with ECR repository URI..."
docker tag backend/api:$API_VERSION $REPO_URI:$API_VERSION
echo "Finished tagging image"

echo "Pushing image to ECR repository $REPO_URI ..."
docker push $REPO_URI:$API_VERSION
echo "Finished pushing image to ECR at $REPO_URI:$API_VERSION"

# Task definition file
TDFILE=.aws/lcog-team-staging-backend-task-definition.json

# Check if jq is installed and task definition can be updated automatically
echo "Checking if jq is installed..."
if ! command -v jq >/dev/null; then
  echo "\nIt looks like jq is not installed; cannot automatically update the image version in the task definition file $TDFILE.\n\nEdit the task definition file manually and then run the ECS deployment commands manually."
  exit 1
else
    echo "Updating the image version in task definition file $TDFILE ..."
  # Update task definition with new image version
    cat <<< "$(jq --arg image "$REPO_URI:$API_VERSION" '.containerDefinitions[0].image = $image' $TDFILE)" > "$TDFILE"
    echo "Finished updating image version $REPO_URI:$API_VERSION in task definition $TDFILE"
fi

# Update the task definition
echo "Registering updated task definition in ECS..."
aws ecs register-task-definition \
--cli-input-json "file://./$TDFILE" \
--no-cli-pager \
--profile $AWS_PROFILE
echo "Finished registering updated task definition $TDFILE"

# Update the service deployment to use the latest version of the task definition
echo "Starting deployment for ECS service..."
aws ecs update-service \
--cluster lcog-team-staging-ecs-cluster \
--service lcog-team-staging-backend-service \
--task-definition lcog-team-app-staging-backend-td \
--no-cli-pager \
--profile $AWS_PROFILE
echo "ECS service deployment started"

echo "\n\nGit commit message: Update API image to version $API_VERSION"