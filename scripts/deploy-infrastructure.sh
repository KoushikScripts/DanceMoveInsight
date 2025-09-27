#!/bin/bash

# Deploy AWS infrastructure using CloudFormation
# Usage: ./scripts/deploy-infrastructure.sh [AWS_REGION] [ENVIRONMENT]

set -e

# Configuration
PROJECT_NAME="dance-pose-detector"
AWS_REGION=${1:-us-east-1}
ENVIRONMENT=${2:-production}
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}"

echo "🎭 Dance Pose Detector - Infrastructure Deployment"
echo "=================================================="
echo "AWS Region: ${AWS_REGION}"
echo "Environment: ${ENVIRONMENT}"
echo "Stack Name: ${STACK_NAME}"
echo "=================================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Validate CloudFormation template
echo "✅ Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://aws/cloudformation-template.yml \
    --region ${AWS_REGION}

# Deploy or update stack
echo "🚀 Deploying infrastructure stack..."
aws cloudformation deploy \
    --template-file aws/cloudformation-template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        ProjectName=${PROJECT_NAME} \
        Environment=${ENVIRONMENT} \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${AWS_REGION} \
    --no-fail-on-empty-changeset

# Get stack outputs
echo "📋 Stack outputs:"
aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

echo "✅ Infrastructure deployment completed!"

# Save important outputs to file
echo "💾 Saving deployment info..."
cat > deployment-info.json << EOF
{
  "project_name": "${PROJECT_NAME}",
  "environment": "${ENVIRONMENT}",
  "aws_region": "${AWS_REGION}",
  "stack_name": "${STACK_NAME}",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "📄 Deployment info saved to deployment-info.json"