#!/bin/bash

# Deploy ECS service
# Usage: ./scripts/deploy-service.sh [AWS_REGION] [ENVIRONMENT]

set -e

# Configuration
PROJECT_NAME="dance-pose-detector"
AWS_REGION=${1:-us-east-1}
ENVIRONMENT=${2:-production}
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}"
SERVICE_NAME="${PROJECT_NAME}-service"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🎭 Dance Pose Detector - Service Deployment"
echo "============================================"
echo "AWS Region: ${AWS_REGION}"
echo "Environment: ${ENVIRONMENT}"
echo "Service Name: ${SERVICE_NAME}"
echo "============================================"

# Get stack outputs
echo "📋 Getting infrastructure details..."
VPC_ID=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`VPCId`].OutputValue' \
    --output text)

SUBNET1_ID=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnet1Id`].OutputValue' \
    --output text)

SUBNET2_ID=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnet2Id`].OutputValue' \
    --output text)

CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
    --output text)

ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
    --output text)

# Update task definition with correct values
echo "📝 Updating task definition..."
sed -e "s/YOUR_ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" \
    -e "s/YOUR_REGION/${AWS_REGION}/g" \
    aws/ecs-task-definition.json > /tmp/task-definition.json

# Register task definition
echo "📋 Registering ECS task definition..."
TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-definition.json \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "✅ Task definition registered: ${TASK_DEFINITION_ARN}"

# Create or update ECS service
echo "🚀 Deploying ECS service..."
if aws ecs describe-services \
    --cluster ${CLUSTER_NAME} \
    --services ${SERVICE_NAME} \
    --region ${AWS_REGION} \
    --query 'services[0].serviceName' \
    --output text 2>/dev/null | grep -q ${SERVICE_NAME}; then
    
    echo "🔄 Updating existing service..."
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --task-definition ${TASK_DEFINITION_ARN} \
        --region ${AWS_REGION} \
        --force-new-deployment
else
    echo "🆕 Creating new service..."
    aws ecs create-service \
        --cluster ${CLUSTER_NAME} \
        --service-name ${SERVICE_NAME} \
        --task-definition ${TASK_DEFINITION_ARN} \
        --desired-count 2 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[${SUBNET1_ID},${SUBNET2_ID}],securityGroups=[$(aws ec2 describe-security-groups --filters Name=group-name,Values=${PROJECT_NAME}-ecs-sg --query 'SecurityGroups[0].GroupId' --output text --region ${AWS_REGION})],assignPublicIp=ENABLED}" \
        --load-balancers "targetGroupArn=$(aws elbv2 describe-target-groups --names ${PROJECT_NAME}-tg --query 'TargetGroups[0].TargetGroupArn' --output text --region ${AWS_REGION}),containerName=dance-pose-api,containerPort=5000" \
        --region ${AWS_REGION}
fi

# Wait for service to be stable
echo "⏳ Waiting for service to stabilize..."
aws ecs wait services-stable \
    --cluster ${CLUSTER_NAME} \
    --services ${SERVICE_NAME} \
    --region ${AWS_REGION}

# Get load balancer URL
ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

echo "✅ Service deployment completed!"
echo "🌐 Application URL: http://${ALB_DNS}"
echo "🏥 Health Check: http://${ALB_DNS}/health"

# Clean up
rm -f /tmp/task-definition.json