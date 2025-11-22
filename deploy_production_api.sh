#!/usr/bin/env bash

# Set strict mode
set -eou pipefail

AWS_PROFILE=${AWS_PROFILE:?Set the AWS_PROFILE variable to your ECS developer profile: export AWS_PROFILE=<AWS profile name>}
echo "Using AWS profile $AWS_PROFILE"

# Update the production task definition
echo "Registering updated production task definition in ECS..."
aws ecs register-task-definition \
--cli-input-json "file://./.aws/lcog-team-production-backend-task-definition.json" \
--no-cli-pager \
--profile $AWS_PROFILE
echo "Finished registering updated production task definition lcog-team-production-backend-task-definition.json"

# Update the service deployment to use the latest version of the task definition
echo "Starting deployment to production..."
aws ecs update-service \
--cluster lcog-team-production-ecs-cluster \
--service lcog-team-production-backend-service \
--task-definition lcog-team-production-backend-td \
--no-cli-pager \
--profile $AWS_PROFILE
echo "Production deployment started"
