import os
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, desc
from app import app, db
from models import User, Project, Category, Comment, Like, Tag, AboutMe, project_tags, GitHubRepository, GitHubRepositoryLanguage
from forms import LoginForm, RegisterForm, ProjectForm, CategoryForm, CommentForm, SearchForm, AboutMeForm, UserPromoteForm, UserDemoteForm, UserActivateForm, UserDeactivateForm
from utils import save_picture, delete_picture, parse_tags, admin_required, super_admin_required, log_admin_action
from github_sync import GitHubSyncService

@app.context_processor
def inject_about_me():
    """Make AboutMe data available to all templates"""
    about_me = AboutMe.query.first()
    return dict(about_me=about_me)

# Public routes
@app.route('/')
def index():
    search_form = SearchForm()
    featured_projects = Project.query.filter_by(is_published=True, is_featured=True).limit(3).all()
    recent_projects = Project.query.filter_by(is_published=True).order_by(desc(Project.created_at)).limit(6).all()
    return render_template('index.html', featured_projects=featured_projects, 
                         recent_projects=recent_projects, search_form=search_form)

@app.route('/projects')
def projects():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    language = request.args.get('language', type=str)
    
    # Get CMS projects
    cms_query = Project.query.filter_by(is_published=True)
    if category_id:
        cms_query = cms_query.filter_by(category_id=category_id)
    
    cms_projects = cms_query.order_by(desc(Project.created_at)).paginate(
        page=page, per_page=6, error_out=False)
    
    # Get GitHub repositories (with error handling)
    github_repos = []
    all_languages = []
    try:
        github_service = GitHubSyncService()
        github_repos = github_service.get_repositories_by_language(language, limit=20)
        all_languages = github_service.get_all_languages()
    except Exception as e:
        print(f"GitHub sync error: {e}")
        # Continue without GitHub data
    
    categories = Category.query.all()
    
    return render_template('portfolio/projects.html', 
                         projects=cms_projects, 
                         github_repos=github_repos,
                         categories=categories, 
                         all_languages=all_languages,
                         current_category=category_id,
                         current_language=language, 
                         search_form=search_form)

@app.route('/project/<int:id>')
def project_detail(id):
    search_form = SearchForm()
    project = Project.query.get_or_404(id)
    
    # Increment view count
    project.views_count += 1
    db.session.commit()
    
    comment_form = CommentForm()
    comments = Comment.query.filter_by(project_id=id).order_by(desc(Comment.created_at)).all()
    
    # Check if current user liked this project
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id, project_id=id).first() is not None
    
    return render_template('portfolio/project_detail.html', project=project, 
                         comment_form=comment_form, comments=comments, 
                         user_liked=user_liked, search_form=search_form)

@app.route('/about')
def about():
    search_form = SearchForm()
    return render_template('portfolio/about.html', search_form=search_form)

@app.route('/search')
def search():
    search_form = SearchForm()
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        projects = Project.query.filter(
            Project.is_published == True,
            or_(
                Project.title.contains(query),
                Project.description.contains(query),
                Project.content.contains(query)
            )
        ).order_by(desc(Project.created_at)).paginate(
            page=page, per_page=6, error_out=False)
    else:
        projects = Project.query.filter_by(is_published=True).paginate(
            page=page, per_page=6, error_out=False)
    
    return render_template('search.html', projects=projects, query=query, search_form=search_form)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page)
        flash('Email ou senha inválidos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Nome de usuário já em uso', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('index'))

# Comment and Like routes
@app.route('/add_comment/<int:project_id>', methods=['POST'])
@login_required
def add_comment(project_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            project_id=project_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comentário adicionado com sucesso!', 'success')
    return redirect(url_for('project_detail', id=project_id))

@app.route('/toggle_like/<int:project_id>', methods=['POST'])
@login_required
def toggle_like(project_id):
    project = Project.query.get_or_404(project_id)
    like = Like.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    
    if like:
        db.session.delete(like)
        liked = False
    else:
        like = Like(user_id=current_user.id, project_id=project_id)
        db.session.add(like)
        liked = True
    
    db.session.commit()
    return jsonify({
        'liked': liked,
        'likes_count': project.likes_count
    })

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    total_projects = Project.query.count()
    published_projects = Project.query.filter_by(is_published=True).count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    recent_projects = Project.query.order_by(desc(Project.created_at)).limit(5).all()
    recent_comments = Comment.query.order_by(desc(Comment.created_at)).limit(5).all()
    
    # Get GitHub sync information
    github_service = GitHubSyncService()
    last_sync = github_service.get_last_sync_info('cDorth')
    github_repos_count = GitHubRepository.query.count()
    
    return render_template('admin/dashboard.html', 
                         total_projects=total_projects,
                         published_projects=published_projects,
                         total_comments=total_comments,
                         total_likes=total_likes,
                         recent_projects=recent_projects,
                         recent_comments=recent_comments,
                         last_github_sync=last_sync,
                         github_repos_count=github_repos_count)

@app.route('/admin/projects')
@login_required
def admin_projects():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(desc(Project.created_at)).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def admin_new_project():
    if not current_user.is_admin:
        abort(403)
    
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            demo_url=form.demo_url.data,
            github_url=form.github_url.data,
            category_id=form.category_id.data if form.category_id.data else None,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data
        )
        
        if form.image.data:
            picture_file = save_picture(form.image.data)
            project.image_filename = picture_file
        
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Handle tags
        tags_list = parse_tags(form.tags.data)
        for tag_name in tags_list:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            project.tags.append(tag)
        
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html', form=form, title='New Project')

@app.route('/admin/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(id):
    if not current_user.is_admin:
        abort(403)
    
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.content = form.content.data
        project.demo_url = form.demo_url.data
        project.github_url = form.github_url.data
        project.category_id = form.category_id.data if form.category_id.data else None
        project.is_published = form.is_published.data
        project.is_featured = form.is_featured.data
        
        if form.image.data:
            if project.image_filename:
                delete_picture(project.image_filename)
            picture_file = save_picture(form.image.data)
            project.image_filename = picture_file
        
        # Clear existing tags and add new ones
        project.tags.clear()
        tags_list = parse_tags(form.tags.data)
        for tag_name in tags_list:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            project.tags.append(tag)
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    # Pre-populate tags field
    form.tags.data = ', '.join([tag.name for tag in project.tags])
    
    return render_template('admin/project_form.html', form=form, project=project, title='Edit Project')

@app.route('/admin/project/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_project(id):
    if not current_user.is_admin:
        abort(403)
    
    project = Project.query.get_or_404(id)
    
    if project.image_filename:
        delete_picture(project.image_filename)
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    if not current_user.is_admin:
        abort(403)
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/category/new', methods=['GET', 'POST'])
@login_required
def admin_new_category():
    if not current_user.is_admin:
        abort(403)
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='New Category')

@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_about():
    if not current_user.is_admin:
        abort(403)
    
    about_me = AboutMe.query.first()
    if not about_me:
        about_me = AboutMe(title='About Me', content='Write your story here...')
    
    form = AboutMeForm(obj=about_me)
    
    if form.validate_on_submit():
        about_me.title = form.title.data
        about_me.content = form.content.data
        about_me.linkedin_url = form.linkedin_url.data
        about_me.github_url = form.github_url.data
        about_me.email = form.email.data
        about_me.phone = form.phone.data
        
        if form.image.data:
            if about_me.image_filename:
                delete_picture(about_me.image_filename)
            picture_file = save_picture(form.image.data)
            about_me.image_filename = picture_file
        
        if about_me.id:
            db.session.commit()
        else:
            db.session.add(about_me)
            db.session.commit()
        
        flash('About Me updated successfully!', 'success')
        return redirect(url_for('admin_about'))
    
    return render_template('admin/about_form.html', form=form, about_me=about_me)



# Admin User Management Routes
@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin dashboard with user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Get admin logs for audit trail
    from models import AdminLog
    recent_logs = AdminLog.query.order_by(AdminLog.created_at.desc()).limit(10).all()
    
    # Forms for user actions
    promote_form = UserPromoteForm()
    demote_form = UserDemoteForm()
    activate_form = UserActivateForm()
    deactivate_form = UserDeactivateForm()
    
    return render_template('admin/users.html', 
                         title='User Management',
                         users=users, 
                         recent_logs=recent_logs,
                         promote_form=promote_form,
                         demote_form=demote_form,
                         activate_form=activate_form,
                         deactivate_form=deactivate_form)

@app.route('/admin/promote_user', methods=['POST'])
@admin_required
def promote_user():
    """Promote a user to admin"""
    form = UserPromoteForm()
    
    if form.validate_on_submit():
        user_id = int(form.user_id.data)
        target_user = User.query.get_or_404(user_id)
        
        if target_user.is_admin:
            flash('User is already an admin.', 'warning')
        else:
            target_user.is_admin = True
            db.session.commit()
            
            # Log the action
            log_admin_action(
                admin_user=current_user,
                action='promote_to_admin',
                target_user=target_user,
                description=f'User {target_user.email} promoted to admin by {current_user.email}'
            )
            
            flash(f'User {target_user.username} promoted to admin successfully!', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/demote_user', methods=['POST'])
@admin_required
def demote_user():
    """Demote a user from admin (super admin only for other admins)"""
    form = UserDemoteForm()
    
    if form.validate_on_submit():
        user_id = int(form.user_id.data)
        target_user = User.query.get_or_404(user_id)
        
        # Prevent removing super admin privileges
        if target_user.is_super_admin:
            flash('Cannot remove super admin privileges. Super admin is protected.', 'danger')
            return redirect(url_for('admin_users'))
        
        # Only super admin can demote other admins
        if target_user.is_admin and not current_user.is_super_admin:
            flash('Only super admin can demote other administrators.', 'danger')
            return redirect(url_for('admin_users'))
        
        if not target_user.is_admin:
            flash('User is not an admin.', 'warning')
        else:
            target_user.is_admin = False
            db.session.commit()
            
            # Log the action
            log_admin_action(
                admin_user=current_user,
                action='demote_from_admin',
                target_user=target_user,
                description=f'User {target_user.email} demoted from admin by {current_user.email}'
            )
            
            flash(f'User {target_user.username} demoted from admin successfully!', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/deactivate_user', methods=['POST'])
@admin_required
def deactivate_user():
    """Deactivate a user account"""
    form = UserDeactivateForm()
    
    if form.validate_on_submit():
        user_id = int(form.user_id.data)
        target_user = User.query.get_or_404(user_id)
        
        # Prevent deactivating super admin
        if target_user.is_super_admin:
            flash('Cannot deactivate super admin account. Super admin is protected.', 'danger')
            return redirect(url_for('admin_users'))
        
        # Only super admin can deactivate other admins
        if target_user.is_admin and not current_user.is_super_admin:
            flash('Only super admin can deactivate other administrators.', 'danger')
            return redirect(url_for('admin_users'))
        
        if not target_user.is_active:
            flash('User is already deactivated.', 'warning')
        else:
            target_user.is_active = False
            db.session.commit()
            
            # Log the action
            log_admin_action(
                admin_user=current_user,
                action='deactivate_user',
                target_user=target_user,
                description=f'User {target_user.email} deactivated by {current_user.email}'
            )
            
            flash(f'User {target_user.username} deactivated successfully!', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/activate_user', methods=['POST'])
@admin_required
def activate_user():
    """Activate a user account"""
    form = UserActivateForm()
    
    if form.validate_on_submit():
        user_id = int(form.user_id.data)
        target_user = User.query.get_or_404(user_id)
        
        if target_user.is_active:
            flash('User is already active.', 'warning')
        else:
            target_user.is_active = True
            db.session.commit()
            
            # Log the action
            log_admin_action(
                admin_user=current_user,
                action='activate_user',
                target_user=target_user,
                description=f'User {target_user.email} activated by {current_user.email}'
            )
            
            flash(f'User {target_user.username} activated successfully!', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/logs')
@admin_required
def admin_logs():
    """View admin action logs"""
    page = request.args.get('page', 1, type=int)
    
    from models import AdminLog
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False)
    
    return render_template('admin/logs.html', title='Admin Logs', logs=logs)

@app.route('/admin/github-sync', methods=['GET', 'POST'])
@admin_required
def admin_github_sync():
    """Sync GitHub repositories"""
    github_service = GitHubSyncService()
    
    # Get the current authenticated GitHub user
    github_user = None
    username = None
    try:
        github_user_data = github_service.client.get_authenticated_user()
        if github_user_data:
            username = github_user_data.get('login')
            github_user = github_user_data
    except Exception as e:
        flash(f'Failed to get GitHub user info: {e}', 'warning')
    
    if request.method == 'POST':
        sync_type = request.form.get('sync_type', 'authenticated')
        target_username = request.form.get('username', username)
        
        if sync_type == 'public' and target_username:
            # Use public sync for any username
            from github_public_sync import sync_user_public_repos
            success, message, repos_synced = sync_user_public_repos(target_username)
            
            if success:
                flash(f'GitHub public sync completed! Synced {repos_synced} repositories for user {target_username}.', 'success')
            else:
                flash(f'GitHub public sync failed: {message}', 'danger')
        else:
            # Use authenticated sync
            if not username:
                flash('GitHub user not found. Please check your GitHub connection.', 'danger')
            else:
                success, message, repos_synced = github_service.sync_user_repositories(username)
                
                if success:
                    flash(f'GitHub sync completed successfully! Synced {repos_synced} repositories for user {username}.', 'success')
                else:
                    flash(f'GitHub sync failed: {message}', 'danger')
    
    # Get current sync status
    last_sync = github_service.get_last_sync_info(username) if username else None
    github_repos = GitHubRepository.query.order_by(desc(GitHubRepository.last_sync_at)).limit(10).all()
    total_repos = GitHubRepository.query.count()
    all_languages = github_service.get_all_languages()
    
    return render_template('admin/github_sync.html', 
                         last_sync=last_sync,
                         github_repos=github_repos,
                         total_repos=total_repos,
                         all_languages=all_languages,
                         github_user=github_user,
                         username=username)

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# New feature routes
@app.route('/timeline')
def timeline():
    """Career timeline page"""
    return render_template('timeline.html')

@app.route('/skills-comparator')
def skills_comparator():
    """Skills comparison tool"""
    return render_template('skills-comparator.html')
