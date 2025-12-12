#!/bin/bash

# SSL Certificate Initialization Script for Let's Encrypt
# This script should be run ONCE on first deployment to obtain SSL certificates
#
# Two-stage approach:
# 1. Use HTTP-only config to obtain certificate
# 2. Switch to HTTPS config after certificate is obtained

set -e

echo "=== UnLimi HTTPS Certificate Initialization ==="
echo ""

# Configuration
DOMAIN="www.unlimi.top"
EMAIL="your-email@example.com"  # Replace with your email
STAGING=0  # Set to 1 for testing, 0 for production certificates

# Check if email is still default
if [ "$EMAIL" == "your-email@example.com" ]; then
    echo "❌ Error: Please edit this script and set your email address!"
    echo "   Open init-letsencrypt.sh and change EMAIL variable."
    exit 1
fi

echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if certificate already exists
if [ -f "certbot/conf/live/$DOMAIN/fullchain.pem" ]; then
    echo "⚠️  Certificate already exists for $DOMAIN"
    echo "   Run 'docker compose run --rm certbot certificates' to check status"
    echo "   To force renewal, delete certbot/conf/live/$DOMAIN/ first"
    exit 0
fi

# Create required directories
echo "1/7 Creating certificate directories..."
mkdir -p certbot/conf
mkdir -p certbot/www

# Download recommended TLS parameters
echo "2/7 Downloading recommended TLS parameters..."
if [ ! -f "certbot/conf/options-ssl-nginx.conf" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > certbot/conf/options-ssl-nginx.conf
fi

if [ ! -f "certbot/conf/ssl-dhparams.pem" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > certbot/conf/ssl-dhparams.pem
fi

# Backup current nginx config and switch to HTTP-only config
echo "3/7 Switching to HTTP-only nginx configuration..."
if [ -f "frontend/nginx.conf" ]; then
    cp frontend/nginx.conf frontend/nginx.conf.backup
fi
cp frontend/nginx.conf.temp frontend/nginx.conf
echo "✅ Using temporary HTTP-only configuration"

# Stop frontend if running
echo "4/7 Restarting frontend with HTTP-only configuration..."
docker compose stop frontend 2>/dev/null || true
docker compose up -d frontend
sleep 5

# Verify nginx is running
if ! docker compose ps frontend | grep -q "Up"; then
    echo "❌ Error: Frontend container failed to start"
    echo "   Check logs: docker compose logs frontend"
    exit 1
fi
echo "✅ Frontend running with HTTP-only configuration"

# Request certificate
echo "5/7 Requesting Let's Encrypt certificate..."
if [ $STAGING -eq 1 ]; then
    STAGING_ARG="--staging"
    echo "⚠️  Using staging server (test mode)"
else
    STAGING_ARG=""
    echo "✅ Using production server"
fi

if docker compose run --rm --entrypoint "" certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    $STAGING_ARG \
    -d $DOMAIN; then
    echo "✅ Certificate obtained successfully"
else
    echo "❌ Certificate request failed"
    echo "   Restoring original nginx configuration..."
    if [ -f "frontend/nginx.conf.backup" ]; then
        mv frontend/nginx.conf.backup frontend/nginx.conf
    fi
    exit 1
fi

# Restore full nginx configuration (with HTTPS)
echo "6/7 Switching to full HTTPS configuration..."
if [ -f "frontend/nginx.conf.backup" ]; then
    mv frontend/nginx.conf.backup frontend/nginx.conf
else
    echo "⚠️  Warning: No backup found, keeping current config"
fi

# Restart frontend with HTTPS configuration
echo "7/7 Restarting frontend with HTTPS configuration..."
docker compose stop frontend
docker compose up -d frontend
sleep 5

# Start certbot for auto-renewal
docker compose up -d certbot

echo ""
echo "=== Certificate Initialization Complete ==="
echo ""
echo "✅ SSL certificate obtained successfully!"
echo "✅ Your site is now available at: https://$DOMAIN"
echo "✅ Automatic renewal is configured (runs twice daily)"
echo ""
echo "Certificate details:"
docker compose run --rm certbot certificates
echo ""
echo "Testing HTTPS:"
curl -I https://$DOMAIN 2>&1 | head -5 || echo "Note: curl test may fail if DNS not propagated"
echo ""
echo "Manual commands:"
echo "  Renew: docker compose run --rm certbot renew"
echo "  Check: docker compose logs certbot"
echo "  Status: docker compose run --rm certbot certificates"
