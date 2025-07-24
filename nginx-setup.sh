#!/bin/bash

# Nginx Setup Script for api.shashinthalk.cc
# Sets up reverse proxy with SSL certificates

set -e

echo "🔧 Setting up Nginx reverse proxy for api.shashinthalk.cc"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN="api.shashinthalk.cc"
EMAIL="your-email@example.com"  # Update this with your email

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Update system packages
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update

# Install Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Nginx...${NC}"
    apt install -y nginx
else
    echo -e "${GREEN}✅ Nginx is already installed${NC}"
fi

# Install Certbot for SSL certificates
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Certbot for SSL certificates...${NC}"
    apt install -y certbot python3-certbot-nginx
else
    echo -e "${GREEN}✅ Certbot is already installed${NC}"
fi

# Copy Nginx configuration
echo -e "${YELLOW}📝 Setting up Nginx configuration...${NC}"
cp nginx-api.shashinthalk.cc.conf /etc/nginx/sites-available/api.shashinthalk.cc

# Create temporary HTTP-only configuration for initial setup
echo -e "${YELLOW}🔧 Creating temporary HTTP configuration for SSL certificate generation...${NC}"
cat > /etc/nginx/sites-available/api.shashinthalk.cc.temp << 'EOF'
server {
    listen 80;
    server_name api.shashinthalk.cc;
    
    # Allow Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Proxy all other requests to Flask app
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable temporary configuration
ln -sf /etc/nginx/sites-available/api.shashinthalk.cc.temp /etc/nginx/sites-enabled/api.shashinthalk.cc

# Test Nginx configuration
echo -e "${YELLOW}🧪 Testing Nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration is invalid${NC}"
    exit 1
fi

# Reload Nginx
echo -e "${YELLOW}🔄 Reloading Nginx...${NC}"
systemctl reload nginx

# Check if Flask app is running
echo -e "${YELLOW}🔍 Checking if Flask app is running...${NC}"
if curl -f -s http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✅ Flask app is running on port 5001${NC}"
else
    echo -e "${RED}❌ Flask app is not running on port 5001${NC}"
    echo -e "${YELLOW}💡 Please start your Flask app first:${NC}"
    echo "   docker run -d --name flask-qa-container -p 5001:5001 flask-qa-api"
    exit 1
fi

# Test domain resolution
echo -e "${YELLOW}🌐 Testing domain resolution...${NC}"
if dig +short $DOMAIN | grep -q .; then
    echo -e "${GREEN}✅ Domain $DOMAIN resolves correctly${NC}"
else
    echo -e "${RED}❌ Domain $DOMAIN does not resolve${NC}"
    echo -e "${YELLOW}💡 Please ensure your DNS is configured correctly${NC}"
    exit 1
fi

# Generate SSL certificate
echo -e "${YELLOW}🔐 Generating SSL certificate with Let's Encrypt...${NC}"
echo -e "${BLUE}📧 Please update the email address in this script (EMAIL variable)${NC}"
read -p "Enter your email address for SSL certificate: " USER_EMAIL
if [[ -z "$USER_EMAIL" ]]; then
    USER_EMAIL=$EMAIL
fi

if certbot --nginx -d $DOMAIN --email $USER_EMAIL --agree-tos --non-interactive --redirect; then
    echo -e "${GREEN}✅ SSL certificate generated successfully${NC}"
else
    echo -e "${RED}❌ Failed to generate SSL certificate${NC}"
    echo -e "${YELLOW}💡 You can continue with HTTP-only setup for now${NC}"
fi

# Replace with full configuration
echo -e "${YELLOW}🔄 Updating to full Nginx configuration...${NC}"
ln -sf /etc/nginx/sites-available/api.shashinthalk.cc /etc/nginx/sites-enabled/api.shashinthalk.cc

# Test final configuration
if nginx -t; then
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx configuration updated successfully${NC}"
else
    echo -e "${RED}❌ Final configuration is invalid, reverting...${NC}"
    ln -sf /etc/nginx/sites-available/api.shashinthalk.cc.temp /etc/nginx/sites-enabled/api.shashinthalk.cc
    systemctl reload nginx
fi

# Remove temporary configuration file
rm -f /etc/nginx/sites-available/api.shashinthalk.cc.temp

# Test the setup
echo -e "${YELLOW}🧪 Testing the complete setup...${NC}"

# Test HTTP redirect (if HTTPS is set up)
echo "Testing HTTP redirect..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/health)
if [[ "$HTTP_RESPONSE" == "301" ]] || [[ "$HTTP_RESPONSE" == "200" ]]; then
    echo -e "${GREEN}✅ HTTP access working${NC}"
else
    echo -e "${YELLOW}⚠️ HTTP response: $HTTP_RESPONSE${NC}"
fi

# Test HTTPS (if certificate was generated)
if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    echo "Testing HTTPS..."
    HTTPS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
    if [[ "$HTTPS_RESPONSE" == "200" ]]; then
        echo -e "${GREEN}✅ HTTPS access working${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTPS response: $HTTPS_RESPONSE${NC}"
    fi
fi

# Display final status
echo ""
echo -e "${GREEN}🎉 Nginx reverse proxy setup completed!${NC}"
echo ""
echo -e "${BLUE}📍 Your API is now available at:${NC}"
echo "   - HTTP:  http://$DOMAIN"
echo "   - HTTPS: https://$DOMAIN (if SSL was set up)"
echo ""
echo -e "${BLUE}🔍 Test endpoints:${NC}"
echo "   - Health: https://$DOMAIN/health"
echo "   - Query:  https://$DOMAIN/query"
echo ""
echo -e "${BLUE}📊 Useful commands:${NC}"
echo "   - Check Nginx status: systemctl status nginx"
echo "   - View access logs: tail -f /var/log/nginx/api.shashinthalk.cc.access.log"
echo "   - View error logs: tail -f /var/log/nginx/api.shashinthalk.cc.error.log"
echo "   - Test configuration: nginx -t"
echo "   - Reload Nginx: systemctl reload nginx"
echo ""
echo -e "${BLUE}🔐 SSL Certificate:${NC}"
echo "   - Auto-renewal: certbot renew --dry-run"
echo "   - Certificate info: certbot certificates" 