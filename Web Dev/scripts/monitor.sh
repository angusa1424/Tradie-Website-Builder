#!/bin/bash

# Configuration
LOG_FILE="/var/log/3clickbuilder/monitor.log"
ALERT_EMAIL="admin@3clickbuilder.com"

# Create log directory if it doesn't exist
mkdir -p /var/log/3clickbuilder

# Check if the application is running
check_app() {
    if ! systemctl is-active --quiet 3clickbuilder; then
        echo "$(date): Application is down!" >> $LOG_FILE
        systemctl restart 3clickbuilder
        echo "Application restarted" >> $LOG_FILE
    fi
}

# Check disk space
check_disk() {
    DISK_USAGE=$(df -h /var/www/3clickbuilder | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 90 ]; then
        echo "$(date): Disk usage is high: $DISK_USAGE%" >> $LOG_FILE
    fi
}

# Check memory usage
check_memory() {
    MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
        echo "$(date): Memory usage is high: $MEMORY_USAGE%" >> $LOG_FILE
    fi
}

# Check database size
check_database() {
    DB_SIZE=$(du -h /var/www/3clickbuilder/database/3clickbuilder.db | cut -f1)
    echo "$(date): Database size: $DB_SIZE" >> $LOG_FILE
}

# Run all checks
check_app
check_disk
check_memory
check_database

# Rotate logs if they get too large
if [ -f $LOG_FILE ] && [ $(stat -f%z $LOG_FILE) -gt 10485760 ]; then
    mv $LOG_FILE $LOG_FILE.old
    gzip $LOG_FILE.old
fi 