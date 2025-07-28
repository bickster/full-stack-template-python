#!/bin/bash
set -e

# Database Backup Script

BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

echo "Starting database backup at $(date)"

# Create backup
pg_dump -h db -U $POSTGRES_USER -d $POSTGRES_DB > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "Backup completed: ${BACKUP_FILE}.gz"

# Upload to S3 if configured
if [ ! -z "$BACKUP_S3_BUCKET" ] && [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Uploading to S3..."
    aws s3 cp ${BACKUP_FILE}.gz s3://$BACKUP_S3_BUCKET/backups/
    echo "Upload completed"
fi

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup process completed at $(date)"
