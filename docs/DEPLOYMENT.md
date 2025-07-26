# Production Deployment Guide

This guide covers deploying the FullStack Application to production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Environment Configuration](#environment-configuration)
4. [SSL Setup](#ssl-setup)
5. [Deployment Steps](#deployment-steps)
6. [Post-Deployment](#post-deployment)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

- Ubuntu 20.04+ or similar Linux server
- Docker and Docker Compose installed
- Domain name pointed to your server
- At least 2GB RAM and 20GB storage
- SSH access to the server

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git curl wget ufw fail2ban

# Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Configure fail2ban for SSH protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### 3. Create Application User

```bash
# Create dedicated user for the application
sudo adduser --system --group fullstack
sudo usermod -aG docker fullstack
```

## Environment Configuration

### 1. Clone Repository

```bash
# As the fullstack user
sudo -u fullstack -i
cd /home/fullstack
git clone https://github.com/yourusername/fullstack-app.git
cd fullstack-app
```

### 2. Configure Environment Variables

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with your values
nano .env.production
```

**Important variables to update:**
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `POSTGRES_PASSWORD` - Strong database password
- `REDIS_PASSWORD` - Redis password
- Domain names and URLs
- Email configuration
- Monitoring endpoints

### 3. Create Required Directories

```bash
mkdir -p docker/certbot/www
mkdir -p docker/certbot/conf
mkdir -p docker/postgres-backup
```

## SSL Setup

### Automated SSL Setup

```bash
# Run the SSL setup script
sudo ./scripts/setup_ssl.sh
```

### Manual SSL Setup (if needed)

```bash
# Get initial certificate
docker-compose -f docker-compose.production.yml up -d nginx
docker-compose -f docker-compose.production.yml run --rm certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email admin@yourdomain.com \
    --agree-tos \
    --no-eff-email \
    -d yourdomain.com \
    -d www.yourdomain.com
```

## Deployment Steps

### 1. Build and Start Services

```bash
# Build images
docker-compose -f docker-compose.production.yml build

# Start all services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

### 2. Run Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec api alembic upgrade head

# Initialize database (first time only)
docker-compose -f docker-compose.production.yml exec api python scripts/setup_db.py
```

### 3. Collect Static Files (if applicable)

```bash
# If using static file serving
docker-compose -f docker-compose.production.yml exec api python -m app.cli.commands collect-static
```

### 4. Verify Deployment

```bash
# Check health endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/api/v1/health

# Check logs
docker-compose -f docker-compose.production.yml logs -f
```

## Post-Deployment

### 1. Set Up Monitoring

```bash
# Configure Prometheus (if using external)
# Add your server to prometheus.yml targets

# Configure alerts
# Set up alertmanager rules
```

### 2. Set Up Backups

```bash
# Configure automated backups
crontab -e

# Add backup job (daily at 3 AM)
0 3 * * * cd /home/fullstack/fullstack-app && docker-compose -f docker-compose.production.yml exec -T db pg_dump -U postgres fullstack_prod | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz
```

### 3. Configure Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/fullstack-app

# Add configuration
/home/fullstack/fullstack-app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 fullstack fullstack
    sharedscripts
    postrotate
        docker-compose -f /home/fullstack/fullstack-app/docker-compose.production.yml kill -s USR1 nginx
    endscript
}
```

## Monitoring

### Health Checks

- Application: `https://yourdomain.com/health`
- API: `https://yourdomain.com/api/v1/health`
- Metrics: `https://yourdomain.com/metrics` (restricted access)

### Log Monitoring

```bash
# View all logs
docker-compose -f docker-compose.production.yml logs

# View specific service logs
docker-compose -f docker-compose.production.yml logs api
docker-compose -f docker-compose.production.yml logs nginx

# Follow logs
docker-compose -f docker-compose.production.yml logs -f api
```

### Performance Monitoring

- CPU/Memory: `docker stats`
- Database connections: Check PostgreSQL logs
- Response times: Check nginx access logs

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs [service_name]

# Check resource usage
docker system df
df -h
```

#### 2. Database Connection Issues
```bash
# Test database connection
docker-compose -f docker-compose.production.yml exec db pg_isready

# Check database logs
docker-compose -f docker-compose.production.yml logs db
```

#### 3. SSL Certificate Issues
```bash
# Renew certificates manually
docker-compose -f docker-compose.production.yml run --rm certbot renew

# Check certificate status
docker-compose -f docker-compose.production.yml run --rm certbot certificates
```

#### 4. High Memory Usage
```bash
# Check memory usage by container
docker stats --no-stream

# Restart specific service
docker-compose -f docker-compose.production.yml restart api
```

### Emergency Procedures

#### Rollback Deployment
```bash
# Stop current deployment
docker-compose -f docker-compose.production.yml down

# Checkout previous version
git checkout [previous-tag]

# Rebuild and restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

#### Database Recovery
```bash
# Restore from backup
gunzip < /backup/db_20240101.sql.gz | docker-compose -f docker-compose.production.yml exec -T db psql -U postgres fullstack_prod
```

## Security Checklist

- [ ] Changed all default passwords
- [ ] SSL certificates installed and auto-renewal configured
- [ ] Firewall configured and enabled
- [ ] Fail2ban protecting SSH
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented and tested
- [ ] Monitoring and alerting configured
- [ ] Access logs being collected and monitored
- [ ] Rate limiting enabled
- [ ] CORS properly configured

## Maintenance

### Regular Tasks

**Daily:**
- Check application health
- Review error logs
- Verify backups completed

**Weekly:**
- Review metrics and performance
- Check disk usage
- Update dependencies if needed

**Monthly:**
- Security updates
- SSL certificate renewal check
- Review and rotate logs
- Test backup restoration

## Support

For issues or questions:
1. Check logs first
2. Review this documentation
3. Check GitHub issues
4. Contact support team