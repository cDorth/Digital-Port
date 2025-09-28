import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from github_client import GitHubClient, GitHubAPIError
from models import GitHubRepository, GitHubRepositoryLanguage, GitHubSyncLog
from app import db

logger = logging.getLogger(__name__)

class GitHubSyncService:
    """
    Service to sync GitHub repositories and cache them in the database
    """
    
    def __init__(self):
        self.client = GitHubClient()
    
    def sync_user_repositories(self, username: str) -> Tuple[bool, str, int]:
        """
        Sync all repositories for a given username
        Returns: (success: bool, message: str, repositories_synced: int)
        """
        sync_log = GitHubSyncLog()
        sync_log.username = username
        sync_log.status = 'running'
        sync_log.started_at = datetime.utcnow()
        db.session.add(sync_log)
        db.session.commit()
        
        try:
            logger.info(f"Starting GitHub sync for user: {username}")
            
            # Test connection first
            if not self.client.validate_connection():
                error_msg = "GitHub connection validation failed"
                self._update_sync_log(sync_log, 'error', error_msg, 0)
                return False, error_msg, 0
            
            # Fetch repositories from GitHub
            repositories = self.client.get_user_repositories(username)
            
            if not repositories:
                message = f"No repositories found for user {username}"
                self._update_sync_log(sync_log, 'success', None, 0)
                return True, message, 0
            
            synced_count = 0
            errors = []
            
            for repo_data in repositories:
                try:
                    if self._sync_repository(username, repo_data):
                        synced_count += 1
                except Exception as e:
                    error_msg = f"Error syncing repository {repo_data.get('name', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Determine final status
            if errors and synced_count == 0:
                status = 'error'
                message = f"Failed to sync any repositories. Errors: {'; '.join(errors[:3])}"
            elif errors:
                status = 'partial'
                message = f"Synced {synced_count}/{len(repositories)} repositories. Some errors occurred."
            else:
                status = 'success'
                message = f"Successfully synced {synced_count} repositories"
            
            self._update_sync_log(sync_log, status, message if errors else None, synced_count)
            
            logger.info(f"GitHub sync completed for {username}: {message}")
            return status != 'error', message, synced_count
            
        except GitHubAPIError as e:
            error_msg = f"GitHub API error: {str(e)}"
            self._update_sync_log(sync_log, 'error', error_msg, 0)
            logger.error(error_msg)
            return False, error_msg, 0
        except Exception as e:
            error_msg = f"Unexpected error during sync: {str(e)}"
            self._update_sync_log(sync_log, 'error', error_msg, 0)
            logger.error(error_msg)
            return False, error_msg, 0
    
    def _sync_repository(self, username: str, repo_data: Dict) -> bool:
        """
        Sync a single repository to the database
        Returns True if successful, False otherwise
        """
        try:
            github_id = repo_data['id']
            
            # Check if repository already exists
            existing_repo = GitHubRepository.query.filter_by(github_id=github_id).first()
            
            if existing_repo:
                # Update existing repository
                repository = existing_repo
                logger.debug(f"Updating existing repository: {repo_data['name']}")
            else:
                # Create new repository
                repository = GitHubRepository()
                repository.github_id = github_id
                db.session.add(repository)
                logger.debug(f"Creating new repository: {repo_data['name']}")
            
            # Update repository fields
            self._update_repository_from_data(repository, repo_data)
            
            # Fetch and update languages
            self._sync_repository_languages(repository, username, repo_data['name'])
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing repository {repo_data.get('name', 'unknown')}: {e}")
            return False
    
    def _update_repository_from_data(self, repository: GitHubRepository, repo_data: Dict):
        """
        Update repository model with data from GitHub API
        """
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
    
    def _sync_repository_languages(self, repository: GitHubRepository, owner: str, repo_name: str):
        """
        Fetch and update repository languages
        """
        try:
            # Fetch languages from GitHub API
            languages_data = self.client.get_repository_languages(owner, repo_name)
            
            if not languages_data:
                return
            
            # Calculate total bytes for percentage calculation
            total_bytes = sum(languages_data.values())
            
            # Clear existing languages
            GitHubRepositoryLanguage.query.filter_by(repository_id=repository.id).delete()
            
            # Add new languages
            for language, bytes_count in languages_data.items():
                percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                
                lang_record = GitHubRepositoryLanguage()
                lang_record.repository_id = repository.id
                lang_record.language = language
                lang_record.bytes_count = bytes_count
                lang_record.percentage = percentage
                db.session.add(lang_record)
            
            logger.debug(f"Updated {len(languages_data)} languages for {repo_name}")
            
        except Exception as e:
            logger.warning(f"Error syncing languages for {repo_name}: {e}")
    
    def _update_sync_log(self, sync_log: GitHubSyncLog, status: str, error_message: Optional[str], repositories_synced: int):
        """
        Update the sync log with final status
        """
        sync_log.status = status
        sync_log.error_message = error_message
        sync_log.repositories_synced = repositories_synced
        sync_log.completed_at = datetime.utcnow()
        db.session.commit()
    
    def get_repositories_by_language(self, language: Optional[str] = None, limit: int = 50) -> List[GitHubRepository]:
        """
        Get repositories filtered by language
        """
        query = GitHubRepository.query
        
        if language:
            # Join with language table to filter by language
            query = query.join(GitHubRepositoryLanguage).filter(
                GitHubRepositoryLanguage.language == language
            )
        
        # Order by stars and recent activity
        repositories = query.order_by(
            GitHubRepository.stargazers_count.desc(),
            GitHubRepository.pushed_at.desc()
        ).limit(limit).all()
        
        return repositories
    
    def get_all_languages(self) -> List[Dict[str, int]]:
        """
        Get all unique languages across all repositories with counts
        """
        from sqlalchemy import func
        
        languages = db.session.query(
            GitHubRepositoryLanguage.language,
            func.count(GitHubRepository.id).label('repository_count'),
            func.sum(GitHubRepositoryLanguage.bytes_count).label('total_bytes')
        ).join(GitHubRepository).group_by(
            GitHubRepositoryLanguage.language
        ).order_by(
            func.count(GitHubRepository.id).desc()
        ).all()
        
        return [
            {
                'language': lang.language,
                'repository_count': lang.repository_count,
                'total_bytes': lang.total_bytes
            }
            for lang in languages
        ]
    
    def get_last_sync_info(self, username: str) -> Optional[GitHubSyncLog]:
        """
        Get the last sync log for a username
        """
        return GitHubSyncLog.query.filter_by(
            username=username
        ).order_by(GitHubSyncLog.started_at.desc()).first()