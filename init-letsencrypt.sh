#!/bin/bash

# SSL Certificate Initialization Script for Let's Encrypt
# This script should be run ONCE on first deployment to obtain SSL certificates

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

# Create required directories
echo "1/6 Creating certificate directories..."
mkdir -p certbot/conf/live/$DOMAIN
mkdir -p certbot/www

# Download recommended TLS parameters
echo "2/6 Downloading recommended TLS parameters..."
if [ ! -f "certbot/conf/options-ssl-nginx.conf" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > certbot/conf/options-ssl-nginx.conf
fi

if [ ! -f "certbot/conf/ssl-dhparams.pem" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > certbot/conf/ssl-dhparams.pem
fi

# Create dummy certificate for initial nginx startup
echo "3/6 Creating dummy certificate for nginx startup..."
CERT_PATH="certbot/conf/live/$DOMAIN"
if [ ! -f "$CERT_PATH/fullchain.pem" ]; then
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout "$CERT_PATH/privkey.pem" \
        -out "$CERT_PATH/fullchain.pem" \
        -subj "/CN=$DOMAIN"
    echo "✅ Dummy certificate created"
else
    echo "✅ Certificate files already exist"
fi

# Start nginx with dummy certificate
echo "4/6 Starting nginx with dummy certificate..."
docker compose up -d frontend
sleep 5

# Delete dummy certificate
echo "5/6 Removing dummy certificate and requesting real certificate..."
docker compose exec frontend rm -rf /etc/letsencrypt/live/$DOMAIN
docker compose exec frontend rm -rf /etc/letsencrypt/archive/$DOMAIN
docker compose exec frontend rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf

# Request real certificate
echo "6/6 Requesting Let's Encrypt certificate..."
if [ $STAGING -eq 1 ]; then
    STAGING_ARG="--staging"
    echo "⚠️  Using staging server (test mode)"
else
    STAGING_ARG=""
    echo "✅ Using production server"
fi

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    $STAGING_ARG \
    -d $DOMAIN

# Reload nginx with real certificate
echo ""
echo "Reloading nginx with real certificate..."
docker compose exec frontend nginx -s reload

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
echo "To manually renew certificates: docker compose run --rm certbot renew"
echo "To check renewal: docker compose logs certbot"
