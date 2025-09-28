from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    preferred_language = db.Column(db.String(10), default='pt-BR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='category', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    demo_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    comments = db.relationship('Comment', backref='project', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='project', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='project_tags', backref='projects')
    
    @property
    def likes_count(self):
        return Like.query.filter_by(project_id=self.id).count()
    
    @property
    def comments_count(self):
        return Comment.query.filter_by(project_id=self.id).count()

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Association table for many-to-many relationship between Project and Tag
project_tags = db.Table('project_tags',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Ensure a user can only like a project once
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_like'),)

class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# New models for enhanced functionality
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.Integer, nullable=False, default=1)  # 1-10
    experience_years = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # FontAwesome icon class
    color = db.Column(db.String(7), default='#007bff')  # Hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    project_skills = db.relationship('ProjectSkill', backref='skill', lazy=True)
    
    @property
    def projects_count(self):
        return ProjectSkill.query.filter_by(skill_id=self.id).count()

class ProjectSkill(db.Model):
    __tablename__ = 'project_skills'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    proficiency_used = db.Column(db.Integer, default=5)  # 1-10 how much this skill was used
    is_primary = db.Column(db.Boolean, default=False)  # Main technology used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'project', 'achievement', 'education', 'work'
    importance = db.Column(db.Integer, default=1)  # 1-5, for ordering
    image_filename = db.Column(db.String(255))
    external_url = db.Column(db.String(500))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))  # Optional link to project
    event_metadata = db.Column(db.Text)  # JSON for additional data
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    recommended_project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    similarity_score = db.Column(db.Float, default=0.0)  # 0-1 similarity score
    recommendation_type = db.Column(db.String(50), default='content')  # 'content', 'tag', 'category'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source_project = db.relationship('Project', foreign_keys=[source_project_id], backref='generated_recommendations')
    recommended_project = db.relationship('Project', foreign_keys=[recommended_project_id], backref='received_recommendations')

class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    target_user_email = db.Column(db.String(120))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admin_user = db.relationship('User', foreign_keys=[admin_id], backref='admin_logs')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='target_logs')

class GitHubRepository(db.Model):
    __tablename__ = 'github_repositories'
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    html_url = db.Column(db.String(500), nullable=False)
    homepage = db.Column(db.String(500))
    clone_url = db.Column(db.String(500))
    ssh_url = db.Column(db.String(500))
    language = db.Column(db.String(50))  # Primary language
    stargazers_count = db.Column(db.Integer, default=0)
    watchers_count = db.Column(db.Integer, default=0)
    forks_count = db.Column(db.Integer, default=0)
    size = db.Column(db.Integer, default=0)
    default_branch = db.Column(db.String(50), default='main')
    topics = db.Column(db.Text)  # JSON array of topics
    is_fork = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    has_issues = db.Column(db.Boolean, default=True)
    has_projects = db.Column(db.Boolean, default=True)
    has_wiki = db.Column(db.Boolean, default=True)
    archived = db.Column(db.Boolean, default=False)
    disabled = db.Column(db.Boolean, default=False)
    pushed_at = db.Column(db.DateTime)
    created_at_github = db.Column(db.DateTime)
    updated_at_github = db.Column(db.DateTime)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sync_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    languages = db.relationship('GitHubRepositoryLanguage', backref='repository', lazy=True, cascade='all, delete-orphan')
    
    @property
    def language_list(self):
        try:
            return [lang.language for lang in self.languages.all() if lang]
        except:
            return []
    
    @property
    def primary_languages(self):
        try:
            # Return languages sorted by bytes_count descending, limit to top 3
            lang_list = list(self.languages.all())
            return sorted(lang_list, key=lambda x: x.bytes_count, reverse=True)[:3]
        except:
            return []

class GitHubRepositoryLanguage(db.Model):
    __tablename__ = 'github_repository_languages'
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('github_repositories.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    bytes_count = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    
    # Ensure unique repository-language combinations
    __table_args__ = (db.UniqueConstraint('repository_id', 'language', name='unique_repo_language'),)

class GitHubSyncLog(db.Model):
    __tablename__ = 'github_sync_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'error', 'partial'
    repositories_synced = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    @property
    def duration_seconds(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class GitHubCredentials(db.Model):
    __tablename__ = 'github_credentials'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    encrypted_token = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
