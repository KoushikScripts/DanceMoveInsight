#!/bin/bash

# Setup script for AWS deployment
# Usage: ./setup-aws-deployment.sh

set -e

echo "🎭 Dance Pose Detection API - AWS Deployment Setup"
echo "=================================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install it first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    echo "   You'll need:"
    echo "   - AWS Access Key ID"
    echo "   - AWS Secret Access Key"
    echo "   - Default region (e.g., us-east-1)"
    echo "   - Default output format (json)"
    exit 1
fi

# Get AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo "✅ Prerequisites check passed!"
echo "📋 AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "🌍 AWS Region: ${AWS_REGION}"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

# Test Docker build locally
echo "🐳 Testing Docker build..."
if docker build -t dance-pose-detector:test . > /dev/null 2>&1; then
    echo "✅ Docker build successful!"
    docker rmi dance-pose-detector:test > /dev/null 2>&1
else
    echo "❌ Docker build failed. Please check your Dockerfile."
    exit 1
fi

# Create deployment info
cat > deployment-config.json << EOF
{
  "aws_account_id": "${AWS_ACCOUNT_ID}",
  "aws_region": "${AWS_REGION}",
  "project_name": "dance-pose-detector",
  "ecr_repository": "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dance-pose-detector",
  "setup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "💾 Deployment configuration saved to deployment-config.json"

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================================="
echo ""
echo "🚀 Ready to deploy! Choose your deployment option:"
echo ""
echo "1️⃣  Quick deployment (recommended):"
echo "   ./scripts/full-deploy.sh"
echo ""
echo "2️⃣  Step-by-step deployment:"
echo "   ./scripts/deploy-infrastructure.sh"
echo "   ./scripts/build-and-push.sh"
echo "   ./scripts/deploy-service.sh"
echo ""
echo "3️⃣  Test locally first:"
echo "   ./scripts/test-docker.sh"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "💡 Estimated deployment time: 10-15 minutes"
echo "💰 Estimated monthly cost: $20-50 (depending on usage)"
echo ""