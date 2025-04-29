#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/3clickbuilder"
DB_PATH="/var/www/3clickbuilder/database/3clickbuilder.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
sqlite3 $DB_PATH ".dump" > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz" 