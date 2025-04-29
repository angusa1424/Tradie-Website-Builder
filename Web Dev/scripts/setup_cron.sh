#!/bin/bash

# Create cron jobs for maintenance tasks
(crontab -l 2>/dev/null; echo "0 0 * * * /var/www/3clickbuilder/scripts/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * /var/www/3clickbuilder/scripts/monitor.sh") | crontab -

# Make scripts executable
chmod +x /var/www/3clickbuilder/scripts/backup.sh
chmod +x /var/www/3clickbuilder/scripts/monitor.sh

echo "Cron jobs set up successfully!" 