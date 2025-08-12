import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

def save_picture(form_picture, folder='uploads'):
    """Save uploaded picture with random filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Resize image
    output_size = (800, 600)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn

def delete_picture(filename, folder='uploads'):
    """Delete picture file"""
    if filename:
        picture_path = os.path.join(current_app.root_path, 'static', folder, filename)
        if os.path.exists(picture_path):
            os.remove(picture_path)

def parse_tags(tags_string):
    """Parse comma-separated tags string into list"""
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]

# Admin utilities and decorators
from functools import wraps
from flask import abort, request, jsonify
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)
        
        if not current_user.is_admin:
            return abort(403)
            
        if not current_user.active:
            return abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Decorator to require super admin privileges for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)
        
        if not current_user.is_super_admin:
            return abort(403)
            
        if not current_user.active:
            return abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

def log_admin_action(admin_user, action, target_user=None, description=None):
    """Log an administrative action."""
    from app import db
    from models import AdminLog
    
    log_entry = AdminLog(
        admin_id=admin_user.id if admin_user else None,
        action=action,
        target_user_id=target_user.id if target_user else None,
        target_user_email=target_user.email if target_user else None,
        description=description
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return log_entry
