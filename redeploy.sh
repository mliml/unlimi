#!/bin/bash

echo "=== UnLimi Redeploy Script ==="
echo ""

# Verify .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Stop containers
echo "1/7 Stopping containers..."
docker compose down

# Remove database volume (clean start)
echo "2/7 Removing database volume..."
docker volume rm unlimi_postgres_data 2>/dev/null || echo "  (Volume already removed or doesn't exist)"

# Pull latest code
echo "3/7 Pulling latest code from GitHub..."
git pull origin main

# Verify configuration
echo "4/7 Verifying configuration..."
docker compose run --rm backend python verify_config.py
if [ $? -ne 0 ]; then
    echo "❌ Configuration verification failed! Please check your .env file."
    exit 1
fi

# Rebuild backend (no cache to ensure latest code)
echo "5/7 Rebuilding backend Docker image..."
docker compose build --no-cache backend

# Start all services
echo "6/7 Starting all services..."
docker compose up -d

# Wait for services to start
echo "7/7 Waiting for services to start..."
sleep 20

# Show status
echo ""
echo "=== Deployment Status ==="
docker compose ps

echo ""
echo "=== Backend Logs (last 15 lines) ==="
docker compose logs backend --tail 15

echo ""
echo "=== Deployment Complete ==="
echo "Access your application at: http://$(curl -s ifconfig.me)"
echo ""
echo "To view real-time logs: docker compose logs -f"
echo "To stop all services: docker compose down"
