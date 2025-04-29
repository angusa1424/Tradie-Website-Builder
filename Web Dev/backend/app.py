from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
import logging
from .routes import auth, websites, templates, subscriptions, analytics
from .database import init_db
from .utils.error_handlers import handle_error

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Register blueprints
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(websites.websites_bp, url_prefix='/websites')
    app.register_blueprint(templates.templates_bp, url_prefix='/templates')
    app.register_blueprint(subscriptions.subscriptions_bp, url_prefix='/subscriptions')
    app.register_blueprint(analytics.analytics_bp, url_prefix='/analytics')
    
    # Register error handlers
    app.register_error_handler(Exception, handle_error)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    return app

def main():
    """Main function to run the application"""
    try:
        app = create_app()
        
        # Get port from environment variable or use default
        port = int(os.getenv('PORT', 5001))
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.getenv('FLASK_ENV') == 'development'
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == '__main__':
    main() 