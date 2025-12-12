#!/bin/bash
# TideSight Deployment Script for Ubuntu 24.04
# Server: srv1029413.hstgr.cloud (72.60.187.58)

set -e

echo "=========================================="
echo "TideSight Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="tidesight.cloud"
SERVER_IP="72.60.187.58"
SSH_USER="root"
PROJECT_DIR="/opt/tidesight"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing required packages...${NC}"
apt-get install -y \
    curl \
    wget \
    git \
    docker.io \
    docker-compose \
    certbot \
    python3-certbot-nginx \
    ufw

# Start and enable Docker
systemctl start docker
systemctl enable docker

echo -e "${GREEN}Step 3: Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo -e "${GREEN}Step 4: Creating project directory...${NC}"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo -e "${GREEN}Step 5: Cloning repository (if not exists)...${NC}"
if [ ! -d ".git" ]; then
    echo "Please clone your repository to $PROJECT_DIR"
    echo "git clone <your-repo-url> ."
fi

echo -e "${GREEN}Step 6: Creating .env.prod file...${NC}"
if [ ! -f ".env.prod" ]; then
    cat > .env.prod << EOF
# Django Settings
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud

# Database
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0

# Environment
ENVIRONMENT=production
EOF
    echo -e "${GREEN}.env.prod created${NC}"
else
    echo -e "${YELLOW}.env.prod already exists${NC}"
fi

echo -e "${GREEN}Step 7: Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

echo -e "${GREEN}Step 8: Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${GREEN}Step 9: Running migrations...${NC}"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate_schemas --tenant

echo -e "${GREEN}Step 10: Collecting static files...${NC}"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo -e "${GREEN}Step 11: Setting up SSL certificate...${NC}"
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

echo -e "${GREEN}=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo -e "${NC}Domain: https://$DOMAIN"
echo "Server IP: $SERVER_IP"
echo "Project Directory: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "1. Create superuser: docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
echo "2. Create your first tenant from Django Admin"
echo "3. Access the application at https://$DOMAIN"
