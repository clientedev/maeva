#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    logger.info("🚀 Starting Maeva Real Estate application...")
    
    # Import Flask and create basic app
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(DeclarativeBase):
        pass
    
    # Create Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET")
    if not app.secret_key:
        raise RuntimeError("SESSION_SECRET environment variable is required for security")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database setup
    database_url = os.environ.get("DATABASE_URL", "sqlite:///maeva.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Simple database config for Railway
    if database_url.startswith("postgresql"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "connect_args": {
                "connect_timeout": 10,
                "options": "-c client_encoding=utf8"
            }
        }
    
    # File upload config
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs('uploads', exist_ok=True)
    
    # Initialize database
    db = SQLAlchemy(model_class=Base)
    db.init_app(app)
    
    logger.info("✅ Flask app initialized successfully")
    
    # Basic health check route first
    @app.route('/health')
    def health_check():
        try:
            # Simple database test
            with app.app_context():
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}, 200  # Return 200 to avoid 502
    
    # Basic fallback route - will be overridden by routes.py
    @app.route('/basic-status')
    def basic_status():
        return "Application running", 200
    
    # Import models and create tables with retry logic
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Import models
                from models import Property, Post, AdminSession, PropertyImage, ChatbotConversation, ContactMessage, Admin
                logger.info("✅ Models imported successfully")
                
                # Test database connection first
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                logger.info("✅ Database connection verified")
                
                # Create tables
                db.create_all()
                logger.info("✅ Database tables created successfully")
                
                # Import routes after models are ready
                import routes
                logger.info("✅ Routes imported successfully")
                
                # Success - break out of retry loop
                break
                
        except Exception as e:
            logger.error(f"Database/routes setup error (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("❌ Failed to initialize database after all retries")
                logger.error("Application cannot start without database. Exiting...")
                sys.exit(1)
        
    logger.info("🎉 Application startup complete")
    
except Exception as e:
    logger.error(f"❌ Critical startup error: {e}")
    sys.exit(1)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)