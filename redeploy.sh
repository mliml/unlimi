#!/bin/bash

echo "=== UnLimi Redeploy Script ==="
echo ""

# Stop containers
echo "1/6 Stopping containers..."
docker compose down

# Remove database volume (clean start)
echo "2/6 Removing database volume..."
docker volume rm unlimi_postgres_data 2>/dev/null || echo "  (Volume already removed or doesn't exist)"

# Pull latest code
echo "3/6 Pulling latest code from GitHub..."
git pull origin main

# Rebuild backend (no cache to ensure latest code)
echo "4/6 Rebuilding backend Docker image..."
docker compose build --no-cache backend

# Start all services
echo "5/6 Starting all services..."
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
echo "=== Deployment Complete ==="
echo "Access your application at: http://$(curl -s ifconfig.me)"
echo ""
echo "To view real-time logs: docker compose logs -f"
echo "To stop all services: docker compose down"
