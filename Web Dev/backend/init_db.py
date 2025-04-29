import sqlite3
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with all required tables"""
    try:
        # Ensure the database directory exists
        os.makedirs('database', exist_ok=True)
        
        # Connect to SQLite database
        conn = sqlite3.connect('database/3clickbuilder.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            subscription_status TEXT DEFAULT 'free',
            subscription_end_date TIMESTAMP
        )
        ''')
        
        # Create websites table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            business_name TEXT NOT NULL,
            template TEXT NOT NULL,
            content JSON,
            published_url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            is_published BOOLEAN DEFAULT FALSE,
            custom_domain TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create templates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            html_content TEXT NOT NULL,
            css_content TEXT,
            js_content TEXT,
            is_premium BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create subscriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            plan_type TEXT NOT NULL,
            status TEXT NOT NULL,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create website_analytics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS website_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER,
            page_views INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            date DATE,
            FOREIGN KEY (website_id) REFERENCES websites (id)
        )
        ''')
        
        # Create website_versions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS website_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER,
            version_number INTEGER,
            content JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (website_id) REFERENCES websites (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # Create api_keys table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Insert default templates
        default_templates = [
            ('Basic Business', 'A clean and professional template for small businesses', 
             '<!DOCTYPE html><html>...</html>', 'body { font-family: Arial; }', ''),
            ('Portfolio', 'Perfect for showcasing your work and projects',
             '<!DOCTYPE html><html>...</html>', 'body { font-family: Helvetica; }', ''),
            ('Restaurant', 'Ideal for restaurants and food businesses',
             '<!DOCTYPE html><html>...</html>', 'body { font-family: Georgia; }', '')
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO templates (name, description, html_content, css_content, js_content)
        VALUES (?, ?, ?, ?, ?)
        ''', default_templates)
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_db() 