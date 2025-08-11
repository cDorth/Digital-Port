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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
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
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    # Drop all tables and recreate them to handle new columns
    db.drop_all()
    db.create_all()
    
    # Create super admin user
    from models import User, AdminLog
    from werkzeug.security import generate_password_hash
    
    super_admin = User(
        username='superadmin',
        email='admin@admin.com',
        password_hash=generate_password_hash('Admin@123'),
        is_admin=True,
        is_super_admin=True,
        is_active=True,
        full_name='Super Administrator'
    )
    db.session.add(super_admin)
    
    # Log the super admin creation
    log_entry = AdminLog(
        admin_id=None,  # System created
        action='create_super_admin',
        target_user_email='admin@admin.com',
        description='System created super administrator account'
    )
    db.session.add(log_entry)
    db.session.commit()
    logging.info("Super admin user created: admin@admin.com / Admin@123")
