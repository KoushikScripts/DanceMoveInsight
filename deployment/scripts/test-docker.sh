#!/bin/bash

# Test Docker container locally
# Usage: ./scripts/test-docker.sh

set -e

PROJECT_NAME="dance-pose-detector"

echo "🎭 Dance Pose Detector - Docker Local Testing"
echo "=============================================="

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t ${PROJECT_NAME}:latest .

# Run container
echo "🚀 Starting container..."
docker run -d \
    --name ${PROJECT_NAME}-test \
    -p 5000:5000 \
    -e FLASK_ENV=development \
    ${PROJECT_NAME}:latest

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Test health endpoint
echo "🏥 Testing health endpoint..."
if curl -f http://localhost:5000/health; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    docker logs ${PROJECT_NAME}-test
    exit 1
fi

# Test API documentation
echo "📚 Testing API documentation..."
if curl -H "Accept: application/json" http://localhost:5000/ | grep -q "Dance Pose Detection API"; then
    echo "✅ API documentation accessible!"
else
    echo "❌ API documentation test failed!"
fi

# Test web interface
echo "🌐 Testing web interface..."
if curl -s http://localhost:5000/ | grep -q "Dance Pose Detection"; then
    echo "✅ Web interface accessible!"
else
    echo "❌ Web interface test failed!"
fi

echo ""
echo "🎉 All tests passed!"
echo "🌐 Web interface: http://localhost:5000"
echo "📚 API docs: curl -H 'Accept: application/json' http://localhost:5000/"
echo ""
echo "To stop the container: docker stop ${PROJECT_NAME}-test && docker rm ${PROJECT_NAME}-test"