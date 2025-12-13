#!/bin/bash

echo "=== UnLimi Deploy Script (Preserve Data) ==="
echo ""

# Verify .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Pull latest code
echo "1/6 Pulling latest code from GitHub..."
git pull origin main

# Verify configuration
echo "2/6 Verifying configuration..."
docker compose run --rm backend python scripts/verify_config.py
if [ $? -ne 0 ]; then
    echo "❌ Configuration verification failed! Please check your .env file."
    exit 1
fi

# Rebuild backend (no cache to ensure latest code)
echo "3/6 Rebuilding backend Docker image..."
docker compose build --no-cache backend

# Rebuild frontend (landing + app)
echo "4/6 Rebuilding frontend Docker image (landing + app)..."
docker compose build --no-cache frontend

# Restart all services
echo "5/6 Restarting all services..."
docker compose down
docker compose up -d

# Wait for services to start
echo "6/6 Waiting for services to start..."
sleep 20

# Show status
echo ""
echo "=== Deployment Status ==="
docker compose ps

echo ""
echo "=== Backend Logs (last 15 lines) ==="
docker compose logs backend --tail 15

echo ""
echo "=== Frontend Logs (last 10 lines) ==="
docker compose logs frontend --tail 10

echo ""
echo "=== Deployment Complete ==="
echo "Access your application at: https://www.unlimi.top"
echo ""
echo "To view real-time logs: docker compose logs -f"
echo "To stop all services: docker compose down"
