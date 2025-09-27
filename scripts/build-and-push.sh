#!/bin/bash

# Build and push Docker image to AWS ECR
# Usage: ./scripts/build-and-push.sh [AWS_REGION] [AWS_ACCOUNT_ID]

set -e

# Configuration
PROJECT_NAME="dance-pose-detector"
AWS_REGION=${1:-us-east-1}
AWS_ACCOUNT_ID=${2:-$(aws sts get-caller-identity --query Account --output text)}
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}"

echo "🎭 Dance Pose Detector - Docker Build & Push"
echo "=============================================="
echo "AWS Region: ${AWS_REGION}"
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "ECR Repository: ${ECR_REPOSITORY}"
echo "=============================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Login to ECR
echo "🔐 Logging in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY}

# Create ECR repository if it doesn't exist
echo "📦 Ensuring ECR repository exists..."
aws ecr describe-repositories --repository-names ${PROJECT_NAME} --region ${AWS_REGION} > /dev/null 2>&1 || \
aws ecr create-repository --repository-name ${PROJECT_NAME} --region ${AWS_REGION}

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t ${PROJECT_NAME}:latest .

# Tag image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag ${PROJECT_NAME}:latest ${ECR_REPOSITORY}:latest
docker tag ${PROJECT_NAME}:latest ${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)

# Push image to ECR
echo "📤 Pushing image to ECR..."
docker push ${ECR_REPOSITORY}:latest
docker push ${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)

echo "✅ Docker image successfully pushed to ECR!"
echo "📍 Image URI: ${ECR_REPOSITORY}:latest"