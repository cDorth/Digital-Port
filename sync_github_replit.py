#!/usr/bin/env python3
"""
GitHub sync using Replit's connector API
"""
import os
import sys
import json
import requests
import logging
from datetime import datetime
from app import app, db
from models import GitHubRepository, GitHubRepositoryLanguage, GitHubSyncLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_github_token_from_replit():
    """Get GitHub access token from Replit connector API"""
    try:
        hostname = os.environ.get('CONNECTORS_HOSTNAME', 'connectors.replit.com')
        
        # Get auth token for Replit API
        x_replit_token = None
        if os.environ.get('REPL_IDENTITY'):
            x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY')
        elif os.environ.get('WEB_REPL_RENEWAL'):
            x_replit_token = 'depl ' + os.environ.get('WEB_REPL_RENEWAL')
        elif os.environ.get('REPL_IDENTITY_KEY'):
            x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY_KEY')
        
        if not x_replit_token:
            logger.error('No Replit identity token found')
            return None
        
        # Call Replit connector API
        url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github'
        headers = {
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('items') or len(data['items']) == 0:
            logger.error('No GitHub connection found in Replit')
            return None
        
        connection = data['items'][0]
        settings = connection.get('settings', {})
        
        # Try different possible locations for the access token
        access_token = (
            settings.get('access_token') or
            settings.get('oauth', {}).get('credentials', {}).get('access_token') or
            settings.get('token')
        )
        
        if not access_token:
            logger.error('No access token found in GitHub connection')
            return None
        
        logger.info('Successfully retrieved GitHub token from Replit connector')
        return access_token
        
    except Exception as e:
        logger.error(f'Error getting GitHub token from Replit: {e}')
        return None

def sync_repositories():
    """Sync GitHub repositories using Replit's connector"""
    with app.app_context():
        try:
            # Get GitHub token from Replit
            access_token = get_github_token_from_replit()
            if not access_token:
                logger.error("Failed to get GitHub access token from Replit")
                return False
            
            # Setup requests session
            session = requests.Session()
            session.headers.update({
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'ReplitPortfolio/1.0'
            })
            
            # Get authenticated user info
            response = session.get('https://api.github.com/user')
            response.raise_for_status()
            user_info = response.json()
            
            username = user_info.get('login')
            logger.info(f'Syncing repositories for user: {username}')
            
            # Create sync log
            sync_log = GitHubSyncLog()
            sync_log.username = username
            sync_log.status = 'running'
            sync_log.started_at = datetime.utcnow()
            db.session.add(sync_log)
            db.session.commit()
            
            # Get repositories
            repositories = []
            page = 1
            per_page = 100
            
            while True:
                response = session.get(
                    f'https://api.github.com/users/{username}/repos',
                    params={
                        'per_page': per_page,
                        'page': page,
                        'sort': 'updated',
                        'direction': 'desc'
                    }
                )
                response.raise_for_status()
                page_repos = response.json()
                
                if not page_repos:
                    break
                
                repositories.extend(page_repos)
                
                if len(page_repos) < per_page:
                    break
                
                page += 1
            
            logger.info(f'Found {len(repositories)} repositories')
            
            if not repositories:
                sync_log.status = 'success'
                sync_log.repositories_synced = 0
                sync_log.completed_at = datetime.utcnow()
                db.session.commit()
                logger.info("No repositories found")
                return True
            
            synced_count = 0
            errors = []
            
            for repo_data in repositories:
                try:
                    if sync_repository(session, username, repo_data):
                        synced_count += 1
                except Exception as e:
                    error_msg = f"Error syncing {repo_data.get('name', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Update sync log
            sync_log.repositories_synced = synced_count
            sync_log.completed_at = datetime.utcnow()
            
            if errors and synced_count == 0:
                sync_log.status = 'error'
                sync_log.error_message = f"Failed to sync any repositories: {'; '.join(errors[:3])}"
            elif errors:
                sync_log.status = 'partial' 
                sync_log.error_message = f"Some errors occurred: {'; '.join(errors[:3])}"
            else:
                sync_log.status = 'success'
            
            db.session.commit()
            
            logger.info(f"Sync completed: {synced_count}/{len(repositories)} repositories synced")
            return True
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            if 'sync_log' in locals():
                sync_log.status = 'error'
                sync_log.error_message = str(e)
                sync_log.completed_at = datetime.utcnow()
                db.session.commit()
            return False

def sync_repository(session, username, repo_data):
    """Sync a single repository"""
    try:
        github_id = repo_data['id']
        
        # Check if repository exists
        existing_repo = GitHubRepository.query.filter_by(github_id=github_id).first()
        
        if existing_repo:
            repository = existing_repo
            logger.debug(f"Updating existing repository: {repo_data['name']}")
        else:
            repository = GitHubRepository()
            repository.github_id = github_id
            db.session.add(repository)
            logger.debug(f"Creating new repository: {repo_data['name']}")
        
        # Update repository fields
        repository.name = repo_data['name']
        repository.full_name = repo_data['full_name']
        repository.description = repo_data.get('description', '') or ''
        repository.html_url = repo_data['html_url']
        repository.homepage = repo_data.get('homepage')
        repository.clone_url = repo_data.get('clone_url', '')
        repository.ssh_url = repo_data.get('ssh_url', '')
        repository.language = repo_data.get('language')
        repository.stargazers_count = repo_data.get('stargazers_count', 0)
        repository.watchers_count = repo_data.get('watchers_count', 0)
        repository.forks_count = repo_data.get('forks_count', 0)
        repository.size = repo_data.get('size', 0)
        repository.default_branch = repo_data.get('default_branch', 'main')
        repository.topics = json.dumps(repo_data.get('topics', []))
        repository.is_fork = repo_data.get('fork', False)
        repository.is_private = repo_data.get('private', False)
        repository.has_issues = repo_data.get('has_issues', True)
        repository.has_projects = repo_data.get('has_projects', True)
        repository.has_wiki = repo_data.get('has_wiki', True)
        repository.archived = repo_data.get('archived', False)
        repository.disabled = repo_data.get('disabled', False)
        
        # Parse datetime fields
        if repo_data.get('pushed_at'):
            repository.pushed_at = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
        if repo_data.get('created_at'):
            repository.created_at_github = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
        if repo_data.get('updated_at'):
            repository.updated_at_github = datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00'))
        
        repository.last_sync_at = datetime.utcnow()
        
        # Commit repository first to get ID
        db.session.commit()
        
        # Sync languages after repository is committed
        try:
            lang_response = session.get(f"https://api.github.com/repos/{username}/{repo_data['name']}/languages")
            if lang_response.status_code == 200:
                languages_data = lang_response.json()
                
                if languages_data:
                    # Clear existing languages for this repository
                    GitHubRepositoryLanguage.query.filter_by(repository_id=repository.id).delete()
                    
                    # Calculate total bytes
                    total_bytes = sum(languages_data.values())
                    
                    # Add new languages
                    for language, bytes_count in languages_data.items():
                        percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                        
                        lang_record = GitHubRepositoryLanguage()
                        lang_record.repository_id = repository.id
                        lang_record.language = language
                        lang_record.bytes_count = bytes_count
                        lang_record.percentage = percentage
                        db.session.add(lang_record)
                    
                    # Commit languages
                    db.session.commit()
        except Exception as e:
            logger.warning(f"Error syncing languages for {repo_data['name']}: {e}")
            db.session.rollback()
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing repository {repo_data.get('name', 'unknown')}: {e}")
        return False

if __name__ == "__main__":
    success = sync_repositories()
    sys.exit(0 if success else 1)