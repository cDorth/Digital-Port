#!/usr/bin/env python3
"""
Create demo data for the digital portfolio admin system
"""

from app import app, db
from models import User, Project, Category, AboutMe, AdminLog
from werkzeug.security import generate_password_hash
from utils import log_admin_action
import datetime

def create_demo_data():
    """Create demo users and content for testing the admin system"""
    
    with app.app_context():
        print("Creating demo data...")
        
        # Create demo users
        demo_users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'full_name': 'John Doe',
                'password': 'password123',
                'is_admin': False,
                'is_active': True
            },
            {
                'username': 'jane_admin',
                'email': 'jane@example.com',
                'full_name': 'Jane Smith',
                'password': 'admin123',
                'is_admin': True,
                'is_active': True
            },
            {
                'username': 'bob_inactive',
                'email': 'bob@example.com',
                'full_name': 'Bob Johnson',
                'password': 'password123',
                'is_admin': False,
                'is_active': False
            }
        ]
        
        created_users = []
        for user_data in demo_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User()
                user.username = user_data['username']
                user.email = user_data['email']
                user.full_name = user_data['full_name']
                user.password_hash = generate_password_hash(user_data['password'])
                user.is_admin = user_data['is_admin']
                user.is_active = user_data['is_active']
                user.is_super_admin = False
                
                db.session.add(user)
                created_users.append(user)
                print(f"Created user: {user.username} ({user.email})")
        
        # Create demo category
        existing_category = Category.query.filter_by(name='Demo Category').first()
        if not existing_category:
            category = Category()
            category.name = 'Demo Category'
            category.description = 'A category for demonstration purposes'
            db.session.add(category)
            print("Created demo category")
        
        # Create About Me content
        existing_about = AboutMe.query.first()
        if not existing_about:
            about = AboutMe()
            about.title = 'Welcome to My Portfolio'
            about.content = '''Hi! I'm a passionate developer who loves creating amazing digital experiences. 
            This portfolio showcases my work and the journey I've taken in the world of technology.
            
            I specialize in web development, with expertise in Python, Flask, and modern frontend technologies.
            When I'm not coding, you can find me exploring new technologies and contributing to open source projects.'''
            about.email = 'contact@portfolio.com'
            about.github_url = 'https://github.com/portfolio'
            about.linkedin_url = 'https://linkedin.com/in/portfolio'
            
            db.session.add(about)
            print("Created About Me content")
        
        # Commit all changes
        db.session.commit()
        
        # Create some demo admin logs
        super_admin = User.query.filter_by(is_super_admin=True).first()
        if super_admin and created_users:
            for user in created_users:
                if user.is_admin:
                    log_entry = AdminLog()
                    log_entry.admin_id = super_admin.id
                    log_entry.action = 'promote_to_admin'
                    log_entry.target_user_id = user.id
                    log_entry.target_user_email = user.email
                    log_entry.description = f'Demo: User {user.email} promoted to admin'
                    log_entry.created_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
                    
                    db.session.add(log_entry)
                
                if not user.is_active:
                    log_entry = AdminLog()
                    log_entry.admin_id = super_admin.id
                    log_entry.action = 'deactivate_user'
                    log_entry.target_user_id = user.id
                    log_entry.target_user_email = user.email
                    log_entry.description = f'Demo: User {user.email} deactivated for demo purposes'
                    log_entry.created_at = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
                    
                    db.session.add(log_entry)
            
            db.session.commit()
            print("Created demo admin logs")
        
        print("\nDemo data creation completed!")
        print("You can now test the admin system with these accounts:")
        print("- Super Admin: admin@admin.com / Admin@123")
        print("- Regular Admin: jane@example.com / admin123")
        print("- Regular User: john@example.com / password123")
        print("- Inactive User: bob@example.com / password123")

if __name__ == '__main__':
    create_demo_data()