import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable must be set")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - PostgreSQL (Replit integrated database)
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL not found - PostgreSQL database required")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    # Create all tables if they don't exist
    db.create_all()
    
    # Superadmin seeding disabled for security
    
    # GitHub credentials configured for on-demand sync
    logging.info("GitHub sync system initialized")
    
    # Auto-configure GitHub credentials if available
    try:
        from github_client import GitHubClient
        client = GitHubClient()
        if not client.validate_connection():
            client.initialize_credentials_from_env()
    except Exception as e:
        logging.debug(f"GitHub credentials auto-setup: {e}")
    
    # Start automatic GitHub synchronization (optional)
    try:
        from auto_sync_scheduler import start_background_sync
        if start_background_sync():
            logging.info("GitHub auto-sync service started")
        else:
            logging.info("GitHub auto-sync not started - configure GITHUB_TOKEN in Secrets to enable")
    except Exception as e:
        logging.warning(f"GitHub auto-sync not available: {e}")
        logging.info("System will continue without GitHub sync")

# Import and initialize API routes
from api_routes import init_api_routes
init_api_routes(app)
