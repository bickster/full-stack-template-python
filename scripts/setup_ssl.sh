#!/bin/bash
set -e

# SSL Certificate Setup Script for Let's Encrypt

echo "🔐 SSL Certificate Setup"
echo "======================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN
read -p "Enter your email for Let's Encrypt notifications: " EMAIL

# Validate inputs
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Domain and email are required!"
    exit 1
fi

echo ""
echo "Setting up SSL for: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Create required directories
mkdir -p docker/certbot/www
mkdir -p docker/certbot/conf

# Update nginx config with actual domain
sed -i "s/yourdomain.com/$DOMAIN/g" docker/nginx-production.conf

# Start nginx temporarily for certificate generation
echo "Starting nginx for certificate validation..."
docker-compose -f docker-compose.production.yml up -d nginx

# Wait for nginx to start
sleep 5

# Get initial certificate
echo "Requesting certificate from Let's Encrypt..."
docker run --rm \
    -v "$PWD/docker/certbot/www:/var/www/certbot" \
    -v "$PWD/docker/certbot/conf:/etc/letsencrypt" \
    certbot/certbot \
    certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Check if successful
if [ $? -eq 0 ]; then
    echo "✅ SSL certificate obtained successfully!"
    
    # Create renewal script
    cat > scripts/renew_ssl.sh << EOF
#!/bin/bash
# SSL Certificate Renewal Script

echo "Renewing SSL certificates..."
docker-compose -f docker-compose.production.yml run --rm certbot renew
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
echo "SSL certificates renewed!"
EOF

    chmod +x scripts/renew_ssl.sh
    
    # Add to crontab for automatic renewal
    echo "Setting up automatic renewal..."
    (crontab -l 2>/dev/null; echo "0 3 * * * cd $PWD && ./scripts/renew_ssl.sh >> /var/log/ssl-renewal.log 2>&1") | crontab -
    
    echo ""
    echo "✅ SSL setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Update your .env.production file with your domain"
    echo "2. Run: docker-compose -f docker-compose.production.yml up -d"
    echo ""
    echo "Automatic renewal has been set up via cron."
    echo "Manual renewal: ./scripts/renew_ssl.sh"
else
    echo "❌ Failed to obtain SSL certificate"
    echo "Please check your domain DNS settings and try again."
    exit 1
fi