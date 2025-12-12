#!/bin/bash

echo "=== UnLimi Deployment Script ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your values."
    exit 1
fi

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build and start containers
echo "Building and starting containers..."
docker compose down
docker compose build --no-cache
docker compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check service status
echo "Checking service status..."
docker compose ps

echo ""
echo "=== Deployment Complete ==="
echo "Access your application at: http://$(curl -s ifconfig.me)"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
