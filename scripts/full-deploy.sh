#!/bin/bash

# Complete deployment script for Dance Pose Detection API
# Usage: ./scripts/full-deploy.sh [AWS_REGION] [ENVIRONMENT]

set -e

# Configuration
AWS_REGION=${1:-us-east-1}
ENVIRONMENT=${2:-production}

echo "🎭 Dance Pose Detector - Complete AWS Deployment"
echo "================================================="
echo "AWS Region: ${AWS_REGION}"
echo "Environment: ${ENVIRONMENT}"
echo "================================================="

# Make scripts executable
chmod +x scripts/*.sh

# Step 1: Deploy infrastructure
echo "📋 Step 1: Deploying AWS infrastructure..."
./scripts/deploy-infrastructure.sh ${AWS_REGION} ${ENVIRONMENT}

# Step 2: Build and push Docker image
echo "🐳 Step 2: Building and pushing Docker image..."
./scripts/build-and-push.sh ${AWS_REGION}

# Step 3: Deploy ECS service
echo "🚀 Step 3: Deploying ECS service..."
./scripts/deploy-service.sh ${AWS_REGION} ${ENVIRONMENT}

# Get final deployment info
STACK_NAME="dance-pose-detector-${ENVIRONMENT}"
ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "====================================="
echo "🌐 Application URL: http://${ALB_DNS}"
echo "🏥 Health Check: http://${ALB_DNS}/health"
echo "📚 API Documentation: http://${ALB_DNS} (with Accept: application/json)"
echo ""
echo "📋 Next Steps:"
echo "1. Test the health endpoint: curl http://${ALB_DNS}/health"
echo "2. Upload a video via the web interface"
echo "3. Monitor logs in CloudWatch: /ecs/dance-pose-detector"
echo "4. Set up custom domain and SSL certificate if needed"
echo ""
echo "💡 Useful Commands:"
echo "- View ECS service: aws ecs describe-services --cluster dance-pose-detector-cluster --services dance-pose-detector-service --region ${AWS_REGION}"
echo "- View logs: aws logs tail /ecs/dance-pose-detector --follow --region ${AWS_REGION}"
echo "- Scale service: aws ecs update-service --cluster dance-pose-detector-cluster --service dance-pose-detector-service --desired-count 3 --region ${AWS_REGION}"
echo ""