import sqlite3
import os
from contextlib import contextmanager
from .utils.error_handlers import handle_error

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/3clickbuilder.db')

def get_db():
    """Get database connection"""
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        
        return conn
    except Exception as e:
        raise handle_error(e)

@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise handle_error(e)
    finally:
        conn.close()

def init_db():
    """Initialize database with required tables"""
    try:
        with db_transaction() as db:
            # Create users table
            db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                subscription_status TEXT DEFAULT 'free',
                subscription_end_date TIMESTAMP
            )
            ''')
            
            # Create websites table
            db.execute('''
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
            db.execute('''
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
            db.execute('''
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
            db.execute('''
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
            db.execute('''
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
            db.execute('''
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
            
    except Exception as e:
        raise handle_error(e)

def execute_query(query, params=None):
    """Execute a database query"""
    try:
        with db_transaction() as db:
            cursor = db.execute(query, params or ())
            return cursor.fetchall()
    except Exception as e:
        raise handle_error(e)

def execute_single_query(query, params=None):
    """Execute a database query and return a single result"""
    try:
        with db_transaction() as db:
            cursor = db.execute(query, params or ())
            return cursor.fetchone()
    except Exception as e:
        raise handle_error(e)

def execute_insert(query, params=None):
    """Execute an insert query and return the last row ID"""
    try:
        with db_transaction() as db:
            cursor = db.execute(query, params or ())
            return cursor.lastrowid
    except Exception as e:
        raise handle_error(e)

def execute_update(query, params=None):
    """Execute an update query and return the number of affected rows"""
    try:
        with db_transaction() as db:
            cursor = db.execute(query, params or ())
            return cursor.rowcount
    except Exception as e:
        raise handle_error(e)

def execute_delete(query, params=None):
    """Execute a delete query and return the number of affected rows"""
    try:
        with db_transaction() as db:
            cursor = db.execute(query, params or ())
            return cursor.rowcount
    except Exception as e:
        raise handle_error(e) 