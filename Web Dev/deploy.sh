#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx sqlite3

# Create project directory
sudo mkdir -p /var/www/3clickbuilder
sudo chown -R $USER:$USER /var/www/3clickbuilder

# Set up Python virtual environment
python3 -m venv /var/www/3clickbuilder/venv
source /var/www/3clickbuilder/venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up Nginx configuration
sudo tee /etc/nginx/sites-available/3clickbuilder << EOF
server {
    listen 80;
    server_name 3clickbuilder.com www.3clickbuilder.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/3clickbuilder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Set up SSL
sudo certbot --nginx -d 3clickbuilder.com -d www.3clickbuilder.com

# Create systemd service
sudo tee /etc/systemd/system/3clickbuilder.service << EOF
[Unit]
Description=3ClickBuilder Flask Application
After=network.target

[Service]
User=$USER
WorkingDirectory=/var/www/3clickbuilder
Environment="PATH=/var/www/3clickbuilder/venv/bin"
ExecStart=/var/www/3clickbuilder/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5001 backend.app:app

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl start 3clickbuilder
sudo systemctl enable 3clickbuilder

# Set up maintenance scripts
mkdir -p /var/www/3clickbuilder/scripts
cp scripts/backup.sh /var/www/3clickbuilder/scripts/
cp scripts/monitor.sh /var/www/3clickbuilder/scripts/
cp scripts/setup_cron.sh /var/www/3clickbuilder/scripts/

# Set up cron jobs
bash /var/www/3clickbuilder/scripts/setup_cron.sh

# Initialize database
python backend/init_db.py

# Run tests
python -m unittest tests/test_app.py

echo "Deployment completed successfully!" 