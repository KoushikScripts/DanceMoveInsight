# PowerShell deployment script for Dance Pose Detection API
# Usage: .\deploy-to-aws.ps1

param(
    [string]$Region = "us-east-1",
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

# Configuration
$ProjectName = "dance-pose-detector"
$StackName = "$ProjectName-$Environment"
$ImageName = "dancemoves:latest"

Write-Host "🎭 Dance Pose Detector - AWS ECS Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "AWS Region: $Region" -ForegroundColor Yellow
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Stack Name: $StackName" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Green

# Check AWS CLI
try {
    $awsVersion = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" --version
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Check AWS configuration
try {
    $identity = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sts get-caller-identity --output json | ConvertFrom-Json
    $AccountId = $identity.Account
    Write-Host "✅ AWS configured for account: $AccountId" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not configured. Please run: aws configure" -ForegroundColor Red
    exit 1
}

# Check Docker image
try {
    docker images $ImageName --format "table {{.Repository}}:{{.Tag}}" | Select-String $ImageName
    Write-Host "✅ Docker image '$ImageName' found" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker image '$ImageName' not found. Please build it first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting deployment process..." -ForegroundColor Cyan

# Step 1: Deploy infrastructure
Write-Host "📋 Step 1: Deploying AWS infrastructure..." -ForegroundColor Yellow
try {
    & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation deploy `
        --template-file aws/cloudformation-template.yml `
        --stack-name $StackName `
        --parameter-overrides ProjectName=$ProjectName Environment=$Environment `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $Region `
        --no-fail-on-empty-changeset
    
    Write-Host "✅ Infrastructure deployed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Infrastructure deployment failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Create ECR repository and push image
Write-Host "🐳 Step 2: Setting up ECR and pushing Docker image..." -ForegroundColor Yellow

# Get ECR repository URI
$EcrUri = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' `
    --output text

Write-Host "📍 ECR Repository: $EcrUri" -ForegroundColor Cyan

# Login to ECR
Write-Host "🔐 Logging in to Amazon ECR..." -ForegroundColor Yellow
$loginCommand = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ecr get-login-password --region $Region
$loginCommand | docker login --username AWS --password-stdin $EcrUri.Split('/')[0]

# Tag and push image
Write-Host "🏷️ Tagging and pushing image..." -ForegroundColor Yellow
docker tag $ImageName "$EcrUri`:latest"
docker tag $ImageName "$EcrUri`:$(Get-Date -Format 'yyyyMMdd-HHmmss')"
docker push "$EcrUri`:latest"
docker push "$EcrUri`:$(Get-Date -Format 'yyyyMMdd-HHmmss')"

Write-Host "✅ Docker image pushed successfully!" -ForegroundColor Green

# Step 3: Update task definition and deploy service
Write-Host "🚀 Step 3: Deploying ECS service..." -ForegroundColor Yellow

# Update task definition with actual values
$taskDefContent = Get-Content "aws/ecs-task-definition.json" -Raw
$taskDefContent = $taskDefContent -replace "YOUR_ACCOUNT_ID", $AccountId
$taskDefContent = $taskDefContent -replace "YOUR_REGION", $Region
$taskDefContent | Out-File "temp-task-definition.json" -Encoding UTF8

# Register task definition
$taskDefArn = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ecs register-task-definition `
    --cli-input-json file://temp-task-definition.json `
    --region $Region `
    --query 'taskDefinition.taskDefinitionArn' `
    --output text

Write-Host "✅ Task definition registered: $taskDefArn" -ForegroundColor Green

# Get cluster and other details
$ClusterName = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' `
    --output text

$ServiceName = "$ProjectName-service"

# Check if service exists
$existingService = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ecs describe-services `
    --cluster $ClusterName `
    --services $ServiceName `
    --region $Region `
    --query 'services[0].serviceName' `
    --output text 2>$null

if ($existingService -eq $ServiceName) {
    Write-Host "🔄 Updating existing service..." -ForegroundColor Yellow
    & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ecs update-service `
        --cluster $ClusterName `
        --service $ServiceName `
        --task-definition $taskDefArn `
        --region $Region `
        --force-new-deployment
} else {
    Write-Host "🆕 Creating new service..." -ForegroundColor Yellow
    
    # Get subnet and security group IDs
    $Subnet1 = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnet1Id`].OutputValue' `
        --output text
    
    $Subnet2 = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnet2Id`].OutputValue' `
        --output text
    
    $SecurityGroup = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 describe-security-groups `
        --filters "Name=group-name,Values=$ProjectName-ecs-sg" `
        --query 'SecurityGroups[0].GroupId' `
        --output text `
        --region $Region
    
    $TargetGroup = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" elbv2 describe-target-groups `
        --names "$ProjectName-tg" `
        --query 'TargetGroups[0].TargetGroupArn' `
        --output text `
        --region $Region
    
    & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ecs create-service `
        --cluster $ClusterName `
        --service-name $ServiceName `
        --task-definition $taskDefArn `
        --desired-count 2 `
        --launch-type FARGATE `
        --network-configuration "awsvpcConfiguration={subnets=[$Subnet1,$Subnet2],securityGroups=[$SecurityGroup],assignPublicIp=ENABLED}" `
        --load-balancers "targetGroupArn=$TargetGroup,containerName=dance-pose-api,containerPort=5000" `
        --region $Region
}

# Wait for service to be stable
Write-Host "⏳ Waiting for service to stabilize..." -ForegroundColor Yellow
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ecs wait services-stable `
    --cluster $ClusterName `
    --services $ServiceName `
    --region $Region

# Get final deployment info
$AlbDns = & "C:\Program Files\Amazon\AWSCLIV2\aws.exe" cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' `
    --output text

# Clean up
Remove-Item "temp-task-definition.json" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "🌐 Application URL: http://$AlbDns" -ForegroundColor Cyan
Write-Host "🏥 Health Check: http://$AlbDns/health" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://$AlbDns (with Accept: application/json)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test the health endpoint: curl http://$AlbDns/health" -ForegroundColor White
Write-Host "2. Upload a video via the web interface" -ForegroundColor White
Write-Host "3. Monitor logs in CloudWatch: /ecs/dance-pose-detector" -ForegroundColor White
Write-Host "4. Set up custom domain and SSL certificate if needed" -ForegroundColor White
Write-Host ""
Write-Host "💡 Useful Commands:" -ForegroundColor Yellow
Write-Host "- View ECS service: aws ecs describe-services --cluster $ClusterName --services $ServiceName --region $Region" -ForegroundColor Gray
Write-Host "- View logs: aws logs tail /ecs/dance-pose-detector --follow --region $Region" -ForegroundColor Gray
Write-Host "- Scale service: aws ecs update-service --cluster $ClusterName --service $ServiceName --desired-count 3 --region $Region" -ForegroundColor Gray
Write-Host ""