# 🚀 Dance Pose Detection API - AWS Deployment Guide

This guide walks you through deploying the Dance Pose Detection API to AWS using Docker containers, ECS Fargate, and CloudFormation.

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally

### 2. Required AWS Permissions
Your AWS user/role needs permissions for:
- ECR (Elastic Container Registry)
- ECS (Elastic Container Service)
- CloudFormation
- VPC, EC2, ALB
- IAM roles and policies
- CloudWatch Logs
- Secrets Manager
- S3

### 3. Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

## 🚀 Quick Deployment

### Option 1: One-Command Deployment
```bash
# Deploy everything to us-east-1 production environment
./scripts/full-deploy.sh

# Deploy to specific region and environment
./scripts/full-deploy.sh us-west-2 staging
```

### Option 2: Step-by-Step Deployment

#### Step 1: Deploy Infrastructure
```bash
./scripts/deploy-infrastructure.sh us-east-1 production
```

#### Step 2: Build and Push Docker Image
```bash
./scripts/build-and-push.sh us-east-1
```

#### Step 3: Deploy ECS Service
```bash
./scripts/deploy-service.sh us-east-1 production
```

## 🧪 Local Testing

### Test Docker Container Locally
```bash
./scripts/test-docker.sh
```

### Test with Docker Compose
```bash
# Development environment
docker-compose up

# Production environment
docker-compose -f docker-compose.prod.yml up
```

## 🏗️ Architecture Overview

### AWS Resources Created

1. **VPC & Networking**
   - VPC with public subnets in 2 AZs
   - Internet Gateway and Route Tables
   - Security Groups for ALB and ECS

2. **Container Infrastructure**
   - ECR Repository for Docker images
   - ECS Fargate Cluster
   - ECS Service with auto-scaling

3. **Load Balancing**
   - Application Load Balancer (ALB)
   - Target Group with health checks
   - HTTP listener on port 80

4. **Storage & Secrets**
   - S3 bucket for file storage
   - Secrets Manager for sensitive data
   - CloudWatch Logs for monitoring

### Container Configuration
- **CPU**: 1 vCPU (1024 units)
- **Memory**: 2 GB (2048 MB)
- **Port**: 5000 (mapped to ALB port 80)
- **Health Check**: `/health` endpoint
- **Auto Scaling**: 2-10 tasks based on CPU/memory

## 🔧 Configuration

### Environment Variables
```bash
FLASK_ENV=production          # Environment mode
HOST=0.0.0.0                 # Bind host
PORT=5000                    # Container port
MAX_CONTENT_LENGTH=104857600 # 100MB file limit
RESULT_RETENTION_DAYS=7      # Result cleanup period
SECRET_KEY=<generated>       # Flask secret key
```

### Resource Limits
- **File Upload**: 100MB maximum
- **Memory**: 2GB per container
- **CPU**: 1 vCPU per container
- **Storage**: 7-day retention for results

## 📊 Monitoring & Logging

### CloudWatch Logs
```bash
# View logs
aws logs tail /ecs/dance-pose-detector --follow --region us-east-1

# View specific log stream
aws logs describe-log-streams --log-group-name /ecs/dance-pose-detector --region us-east-1
```

### Health Monitoring
- **Health Check URL**: `http://your-alb-dns/health`
- **Check Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Healthy Threshold**: 2 consecutive successes

### Service Monitoring
```bash
# Check service status
aws ecs describe-services --cluster dance-pose-detector-cluster --services dance-pose-detector-service --region us-east-1

# View running tasks
aws ecs list-tasks --cluster dance-pose-detector-cluster --service-name dance-pose-detector-service --region us-east-1
```

## 🔄 Updates & Maintenance

### Deploy New Version
```bash
# Build and push new image
./scripts/build-and-push.sh us-east-1

# Update service (triggers rolling deployment)
./scripts/deploy-service.sh us-east-1 production
```

### Scale Service
```bash
# Scale to 5 tasks
aws ecs update-service \
    --cluster dance-pose-detector-cluster \
    --service dance-pose-detector-service \
    --desired-count 5 \
    --region us-east-1
```

### Update Configuration
```bash
# Update CloudFormation stack
aws cloudformation deploy \
    --template-file aws/cloudformation-template.yml \
    --stack-name dance-pose-detector-production \
    --parameter-overrides ProjectName=dance-pose-detector Environment=production \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1
```

## 🔒 Security Best Practices

### Container Security
- Non-root user in container
- Minimal base image (Python slim)
- Security headers in production
- Input validation and file type checking

### AWS Security
- VPC with private subnets for ECS tasks
- Security groups with minimal required access
- IAM roles with least privilege
- Secrets stored in AWS Secrets Manager
- S3 bucket with restricted access

### Network Security
- ALB with security groups
- HTTPS termination at ALB (add SSL certificate)
- Private container communication
- No direct internet access to containers

## 💰 Cost Optimization

### Fargate Spot
- Uses Fargate Spot instances (80% cost savings)
- Automatic failover to regular Fargate
- Suitable for fault-tolerant workloads

### Resource Optimization
- Right-sized containers (1 vCPU, 2GB RAM)
- Auto-scaling based on demand
- S3 lifecycle policies for old files
- CloudWatch log retention (7 days)

### Cost Monitoring
```bash
# View ECS costs
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check ECS service events
aws ecs describe-services --cluster dance-pose-detector-cluster --services dance-pose-detector-service --region us-east-1

# Check task logs
aws logs tail /ecs/dance-pose-detector --follow --region us-east-1
```

#### 2. Health Check Failures
```bash
# Test health endpoint directly
curl http://your-alb-dns/health

# Check target group health
aws elbv2 describe-target-health --target-group-arn your-target-group-arn --region us-east-1
```

#### 3. Image Pull Errors
```bash
# Check ECR repository
aws ecr describe-repositories --repository-names dance-pose-detector --region us-east-1

# Re-push image
./scripts/build-and-push.sh us-east-1
```

#### 4. Permission Issues
```bash
# Check IAM roles
aws iam get-role --role-name dance-pose-detector-ecs-execution-role
aws iam get-role --role-name dance-pose-detector-ecs-task-role
```

### Debug Commands
```bash
# Connect to running container (if needed)
aws ecs execute-command \
    --cluster dance-pose-detector-cluster \
    --task task-id \
    --container dance-pose-api \
    --interactive \
    --command "/bin/bash"
```

## 🔄 Cleanup

### Remove All Resources
```bash
# Delete ECS service
aws ecs update-service --cluster dance-pose-detector-cluster --service dance-pose-detector-service --desired-count 0 --region us-east-1
aws ecs delete-service --cluster dance-pose-detector-cluster --service dance-pose-detector-service --region us-east-1

# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name dance-pose-detector-production --region us-east-1

# Delete ECR images
aws ecr batch-delete-image --repository-name dance-pose-detector --image-ids imageTag=latest --region us-east-1
```

## 📞 Support

### Useful Resources
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Fargate Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)

### Getting Help
1. Check CloudWatch logs for errors
2. Verify AWS permissions
3. Test locally with Docker first
4. Check AWS service limits
5. Review security group rules

## 🎉 Success!

Once deployed, your Dance Pose Detection API will be available at:
- **Web Interface**: `http://your-alb-dns`
- **API Endpoint**: `http://your-alb-dns/upload`
- **Health Check**: `http://your-alb-dns/health`
- **API Documentation**: `http://your-alb-dns` (with `Accept: application/json`)

The system is now ready for production use with:
- ✅ High availability across multiple AZs
- ✅ Auto-scaling based on demand
- ✅ Load balancing and health checks
- ✅ Secure container deployment
- ✅ Centralized logging and monitoring
- ✅ Cost-optimized with Fargate Spot