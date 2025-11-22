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
aws ecr get-login-password --profile "$AWS_PROFILE" \
  | docker login --username AWS --password-stdin 311127195930.dkr.ecr.us-west-2.amazonaws.com

# Build and push the container image using Docker CLI
# Use current date and short form of Git HEAD commit SHA for API version number:
# YYYY.MM.DD-1a2b3c4
API_VERSION=$(date -I | tr - .)-$(git rev-parse --short HEAD)
echo "Building API image with version $API_VERSION ..."
docker build -t "backend/api:$API_VERSION" .
echo "Finished building backend/api:$API_VERSION"

echo "Tagging image with ECR repository URI..."
docker tag "backend/api:$API_VERSION" "$REPO_URI:$API_VERSION"
echo "Finished tagging image"

echo "Pushing image to ECR repository $REPO_URI ..."
docker push "$REPO_URI:$API_VERSION"
echo "Finished pushing image to ECR at $REPO_URI:$API_VERSION"

# Task definition files
TDFILE_STAGING=.aws/lcog-team-staging-backend-task-definition.json
TDFILE_PRODUCTION=.aws/lcog-team-production-backend-task-definition.json

# Check if jq is installed and task definition can be updated automatically
echo "Checking if jq is installed..."
if ! command -v jq >/dev/null; then
  echo -e "\nIt looks like jq is not installed; cannot automatically update the image version in the task definition files.\n\nEdit the task definition files manually and then run the ECS deployment commands manually."
  exit 1
else
    echo "Updating the image version in task definition file $TDFILE_STAGING ..."
  # Update task definition with new image version
    # Update image version for main Django container
    cat <<< "$(jq --arg image "$REPO_URI:$API_VERSION" '.containerDefinitions[0].image = $image' $TDFILE_STAGING)" > "$TDFILE_STAGING"
    # Update image version for migrations container
    cat <<< "$(jq --arg image "$REPO_URI:$API_VERSION" '.containerDefinitions[2].image = $image' $TDFILE_STAGING)" > "$TDFILE_STAGING"
    echo "Finished updating image version $REPO_URI:$API_VERSION in task definition $TDFILE_STAGING"
    
    echo "Updating the image version in task definition file $TDFILE_PRODUCTION ..."
  # Update task definition with new image version
    # Update image version for main Django container
    cat <<< "$(jq --arg image "$REPO_URI:$API_VERSION" '.containerDefinitions[0].image = $image' $TDFILE_PRODUCTION)" > "$TDFILE_PRODUCTION"
    # Update image version for migrations container
    cat <<< "$(jq --arg image "$REPO_URI:$API_VERSION" '.containerDefinitions[2].image = $image' $TDFILE_PRODUCTION)" > "$TDFILE_PRODUCTION"
    echo "Finished updating image version $REPO_URI:$API_VERSION in task definition $TDFILE_PRODUCTION"
fi

# Update the task definition
echo "Registering updated staging task definition in ECS..."
aws ecs register-task-definition \
--cli-input-json "file://./$TDFILE_STAGING" \
--no-cli-pager \
--profile $AWS_PROFILE
echo "Finished registering updated staging task definition $TDFILE_STAGING"

# Update the service deployment to use the latest version of the task definition
echo "Starting deployment to staging..."
aws ecs update-service \
--cluster lcog-team-staging-ecs-cluster \
--service lcog-team-staging-backend-service \
--task-definition lcog-team-app-staging-backend-td \
--no-cli-pager \
--profile $AWS_PROFILE
echo "Staging deployment started"

echo -e "\nGit commit message: Update API image to version $API_VERSION"