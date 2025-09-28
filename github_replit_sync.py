#!/usr/bin/env python3
"""
GitHub sync using Replit's GitHub integration
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

class ReplitGitHubClient:
    """GitHub client using Replit's connector integration"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self._access_token = None
    
    def _get_replit_github_token(self):
        """Get GitHub access token from Replit connector"""
        # Try environment variables that might be set by the Replit connector
        token_candidates = [
            os.environ.get('GITHUB_TOKEN'),
            os.environ.get('GITHUB_ACCESS_TOKEN'),
            os.environ.get('CONNECTOR_GITHUB_TOKEN'),
            os.environ.get('REPLIT_GITHUB_TOKEN')
        ]
        
        for token in token_candidates:
            if token:
                logger.info(f"Found GitHub token from environment")
                return token
        
        logger.error("No GitHub token found in environment variables")
        return None
    
    def get_authenticated_user(self):
        """Get the authenticated GitHub user"""
        token = self._get_replit_github_token()
        if not token:
            return None
        
        try:
            response = self.session.get(
                f"{self.base_url}/user",
                headers={
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'ReplitPortfolio/1.0'
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting authenticated user: {e}")
            return None
    
    def get_user_repositories(self, username):
        """Get repositories for a user"""
        token = self._get_replit_github_token()
        if not token:
            return []
        
        try:
            repositories = []
            page = 1
            per_page = 100
            
            while True:
                response = self.session.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers={
                        'Authorization': f'token {token}',
                        'Accept': 'application/vnd.github.v3+json',
                        'User-Agent': 'ReplitPortfolio/1.0'
                    },
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
            
            logger.info(f"Fetched {len(repositories)} repositories for {username}")
            return repositories
            
        except Exception as e:
            logger.error(f"Error fetching repositories: {e}")
            return []
    
    def get_repository_languages(self, owner, repo):
        """Get languages for a repository"""
        token = self._get_replit_github_token()
        if not token:
            return {}
        
        try:
            response = self.session.get(
                f"{self.base_url}/repos/{owner}/{repo}/languages",
                headers={
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'ReplitPortfolio/1.0'
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error fetching languages for {owner}/{repo}: {e}")
            return {}

def sync_repositories():
    """Sync GitHub repositories using Replit's integration"""
    with app.app_context():
        try:
            client = ReplitGitHubClient()
            
            # Get authenticated user info
            user_info = client.get_authenticated_user()
            if not user_info:
                logger.error("Failed to get authenticated user - check GitHub connection")
                return False
            
            username = user_info.get('login')
            logger.info(f"Syncing repositories for user: {username}")
            
            # Create sync log
            sync_log = GitHubSyncLog()
            sync_log.username = username
            sync_log.status = 'running'
            sync_log.started_at = datetime.utcnow()
            db.session.add(sync_log)
            db.session.commit()
            
            # Get repositories
            repositories = client.get_user_repositories(username)
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
                    if sync_repository(client, username, repo_data):
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
            return False

def sync_repository(client, username, repo_data):
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
        repository.description = repo_data.get('description', '')
        repository.html_url = repo_data['html_url']
        repository.homepage = repo_data.get('homepage')
        repository.clone_url = repo_data['clone_url']
        repository.ssh_url = repo_data['ssh_url']
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
        
        # Sync languages
        languages_data = client.get_repository_languages(username, repo_data['name'])
        if languages_data:
            # Clear existing languages
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
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing repository {repo_data.get('name', 'unknown')}: {e}")
        return False

if __name__ == "__main__":
    success = sync_repositories()
    sys.exit(0 if success else 1)