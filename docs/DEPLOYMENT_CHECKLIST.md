# Production Deployment Checklist

Use this checklist to ensure a smooth and secure production deployment.

## Pre-Deployment

### Infrastructure
- [ ] Server provisioned with minimum specs (2GB RAM, 20GB storage)
- [ ] Domain name configured and DNS pointing to server
- [ ] SSH access configured with key-based authentication
- [ ] Root login disabled
- [ ] Non-root user created for deployment

### Software Requirements
- [ ] Ubuntu 20.04+ or compatible OS installed
- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Git installed
- [ ] Firewall configured (ports 22, 80, 443 open)
- [ ] Fail2ban installed and configured

## Configuration

### Environment Variables
- [ ] `.env.production` created from `.env.production.example`
- [ ] `SECRET_KEY` generated with strong random value
- [ ] Database passwords changed from defaults
- [ ] Redis password set
- [ ] Email SMTP credentials configured
- [ ] Domain names and URLs updated
- [ ] Sentry DSN configured (if using)
- [ ] AWS credentials configured (if using S3 backups)

### Security Settings
- [ ] All default passwords changed
- [ ] CORS origins properly configured
- [ ] Rate limiting values appropriate for production
- [ ] JWT token expiration times reviewed
- [ ] File upload limits and allowed extensions configured

## Deployment

### Initial Setup
- [ ] Repository cloned to production server
- [ ] Required directories created:
  - [ ] `docker/certbot/www`
  - [ ] `docker/certbot/conf`
  - [ ] `docker/postgres-backup`
- [ ] File permissions set correctly

### SSL Certificate
- [ ] SSL setup script executed successfully
- [ ] Certificates obtained from Let's Encrypt
- [ ] Auto-renewal cron job configured
- [ ] HTTPS redirect working

### Docker Deployment
- [ ] Docker images built successfully
- [ ] All containers started without errors
- [ ] Health checks passing
- [ ] No container restart loops

### Database
- [ ] Database migrations run successfully
- [ ] Initial superuser created
- [ ] Database backup script tested
- [ ] Backup cron job configured

## Post-Deployment Verification

### Application Testing
- [ ] Frontend loads correctly over HTTPS
- [ ] Login functionality working
- [ ] Registration working with email validation
- [ ] Password reset flow tested
- [ ] API endpoints responding correctly
- [ ] WebSocket connections working (if applicable)

### Security Verification
- [ ] SSL certificate valid and properly configured
- [ ] Security headers present in responses
- [ ] Rate limiting working on auth endpoints
- [ ] CORS properly restricting origins
- [ ] No sensitive data in logs
- [ ] Debug mode disabled

### Performance Checks
- [ ] Page load times acceptable
- [ ] API response times < 200ms
- [ ] Database queries optimized
- [ ] Static assets being cached
- [ ] Gzip compression enabled

### Monitoring Setup
- [ ] Prometheus metrics accessible (restricted)
- [ ] Health check endpoints responding
- [ ] Logs being collected properly
- [ ] Error tracking configured (Sentry)
- [ ] Uptime monitoring configured

## Backup and Recovery

### Backup Configuration
- [ ] Database backup script working
- [ ] Backup cron job scheduled
- [ ] Backups being stored securely
- [ ] S3 backup upload working (if configured)
- [ ] Old backups being cleaned up

### Recovery Testing
- [ ] Backup restoration process documented
- [ ] Restore process tested with sample backup
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined

## Documentation

### Technical Documentation
- [ ] Deployment process documented
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Database schema documented

### Operational Documentation
- [ ] Runbook created for common issues
- [ ] Emergency contacts listed
- [ ] Escalation procedures defined
- [ ] Maintenance windows defined

## Monitoring and Alerts

### Monitoring Setup
- [ ] Server monitoring (CPU, memory, disk)
- [ ] Application monitoring (response times, errors)
- [ ] Database monitoring (connections, slow queries)
- [ ] Log aggregation configured

### Alert Configuration
- [ ] Critical alerts configured:
  - [ ] Server down
  - [ ] High error rate
  - [ ] Database connection failures
  - [ ] SSL certificate expiration warning
  - [ ] Disk space warning
  - [ ] High memory usage

## Final Checks

### Security Audit
- [ ] Security scan run (OWASP ZAP or similar)
- [ ] Dependency vulnerabilities checked
- [ ] Exposed ports verified
- [ ] Unnecessary services disabled

### Performance Baseline
- [ ] Load testing completed
- [ ] Performance metrics baseline recorded
- [ ] Bottlenecks identified and documented
- [ ] Scaling plan created

### Business Continuity
- [ ] Disaster recovery plan created
- [ ] Data retention policy defined
- [ ] GDPR compliance verified (if applicable)
- [ ] Terms of service and privacy policy updated

## Go-Live

### Final Steps
- [ ] DNS TTL reduced prior to switch
- [ ] Maintenance page prepared
- [ ] Team notified of deployment
- [ ] Rollback plan prepared

### Post Go-Live
- [ ] Application accessible via production URL
- [ ] All features working as expected
- [ ] No critical errors in logs
- [ ] Performance metrics normal
- [ ] Team notified of successful deployment

## Sign-Off

- [ ] Technical Lead approval
- [ ] Security review completed
- [ ] Business stakeholder approval
- [ ] Documentation complete

**Deployment Date:** _______________

**Deployed By:** _______________

**Version/Tag:** _______________

**Notes:**
_________________________________
_________________________________
_________________________________