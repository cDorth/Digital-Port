"""
Seed script to populate the database with initial sample data.
Run this script to add sample categories and a demo project.
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Category, Project, Tag, AboutMe, project_tags
from werkzeug.security import generate_password_hash

def seed_database():
    """Populate the database with initial data"""
    with app.app_context():
        print("Starting database seeding...")
        
        # Create categories
        categories_data = [
            {
                'name': 'Web Development',
                'description': 'Full-stack web applications, websites, and web-based tools.'
            },
            {
                'name': 'Mobile Apps',
                'description': 'iOS and Android applications, cross-platform mobile solutions.'
            },
            {
                'name': 'Data Science',
                'description': 'Data analysis, machine learning, and data visualization projects.'
            },
            {
                'name': 'DevOps',
                'description': 'Infrastructure, deployment, and automation tools.'
            },
            {
                'name': 'UI/UX Design',
                'description': 'User interface design, user experience research, and prototypes.'
            },
            {
                'name': 'Open Source',
                'description': 'Contributions to open source projects and community tools.'
            }
        ]
        
        print("Creating categories...")
        for cat_data in categories_data:
            existing_category = Category.query.filter_by(name=cat_data['name']).first()
            if not existing_category:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                print(f"  - Added category: {cat_data['name']}")
            else:
                print(f"  - Category already exists: {cat_data['name']}")
        
        db.session.commit()
        
        # Create tags
        tags_data = [
            'Python', 'JavaScript', 'React', 'Flask', 'Django', 'Node.js',
            'HTML', 'CSS', 'Bootstrap', 'Tailwind', 'MongoDB', 'PostgreSQL',
            'MySQL', 'Redis', 'Docker', 'AWS', 'Git', 'REST API',
            'GraphQL', 'TypeScript', 'Vue.js', 'Angular', 'Machine Learning',
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Jupyter',
            'Linux', 'Bash', 'CI/CD', 'Kubernetes', 'Microservices'
        ]
        
        print("Creating tags...")
        for tag_name in tags_data:
            existing_tag = Tag.query.filter_by(name=tag_name).first()
            if not existing_tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                print(f"  - Added tag: {tag_name}")
        
        db.session.commit()
        
        # Create sample AboutMe if it doesn't exist
        about_me = AboutMe.query.first()
        if not about_me:
            print("Creating About Me section...")
            about_me = AboutMe(
                title='About Me',
                content='''<p>Welcome to my digital portfolio! I'm a passionate software developer with a love for creating innovative solutions and learning new technologies.</p>

<h3>My Journey</h3>
<p>My journey in software development started with curiosity and has evolved into a professional passion. I enjoy working on diverse projects that challenge me to grow and learn new skills.</p>

<h3>Skills & Expertise</h3>
<ul>
<li><strong>Backend Development:</strong> Python, Flask, Django, Node.js</li>
<li><strong>Frontend Development:</strong> JavaScript, React, Vue.js, HTML5, CSS3</li>
<li><strong>Databases:</strong> PostgreSQL, MongoDB, Redis</li>
<li><strong>DevOps:</strong> Docker, AWS, CI/CD, Linux</li>
<li><strong>Tools:</strong> Git, VS Code, Postman, Figma</li>
</ul>

<h3>What I Do</h3>
<p>I specialize in building full-stack web applications, designing user-friendly interfaces, and implementing scalable backend systems. I'm always eager to take on new challenges and collaborate on exciting projects.</p>

<p>Feel free to explore my projects and get in touch if you'd like to collaborate!</p>''',
                email='admin@portfolio.com',
                linkedin_url='https://linkedin.com/in/yourprofile',
                github_url='https://github.com/yourusername'
            )
            db.session.add(about_me)
            db.session.commit()
            print("  - Created About Me section")
        else:
            print("About Me section already exists")
        
        # Create a sample project if no projects exist
        project_count = Project.query.count()
        if project_count == 0:
            print("Creating sample project...")
            
            # Get the first category and some tags
            web_dev_category = Category.query.filter_by(name='Web Development').first()
            python_tag = Tag.query.filter_by(name='Python').first()
            flask_tag = Tag.query.filter_by(name='Flask').first()
            html_tag = Tag.query.filter_by(name='HTML').first()
            
            sample_project = Project(
                title='Digital Portfolio System',
                description='A comprehensive portfolio management system built with Flask, featuring admin controls, user authentication, and responsive design.',
                content='''<p>This project is a full-featured digital portfolio system that allows users to showcase their work in a professional and organized manner.</p>

<h3>Features</h3>
<ul>
<li>Admin dashboard for content management</li>
<li>User authentication and registration</li>
<li>Project showcase with categories and tags</li>
<li>Comment and like system</li>
<li>Responsive design with Bootstrap</li>
<li>Search functionality</li>
<li>File upload handling</li>
</ul>

<h3>Technology Stack</h3>
<p>Built using modern web technologies including Flask, SQLAlchemy, Bootstrap, and PostgreSQL for a robust and scalable solution.</p>

<h3>Implementation Highlights</h3>
<p>The system implements secure user authentication, efficient database design with proper relationships, and a clean, responsive user interface that works well on all devices.</p>''',
                category_id=web_dev_category.id if web_dev_category else None,
                is_published=True,
                is_featured=True,
                demo_url='#',
                github_url='https://github.com/yourusername/portfolio'
            )
            
            db.session.add(sample_project)
            db.session.flush()  # Get the project ID
            
            # Add tags to the project
            if python_tag:
                sample_project.tags.append(python_tag)
            if flask_tag:
                sample_project.tags.append(flask_tag)
            if html_tag:
                sample_project.tags.append(html_tag)
            
            db.session.commit()
            print("  - Created sample project: Digital Portfolio System")
        else:
            print(f"Projects already exist ({project_count} projects found)")
        
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
