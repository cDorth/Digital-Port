
#!/usr/bin/env python3
"""
GitHub public repository sync without authentication
Para repositórios públicos que não precisam de token
"""
import requests
import json
import logging
from datetime import datetime
from app import app, db
from models import GitHubRepository, GitHubRepositoryLanguage, GitHubSyncLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublicGitHubSync:
    """Sync public GitHub repositories without authentication"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Portfolio-Sync/1.0'
        })
    
    def sync_public_repositories(self, username: str) -> tuple[bool, str, int]:
        """
        Sync public repositories for a username without authentication
        """
        with app.app_context():
            sync_log = GitHubSyncLog()
            sync_log.username = username
            sync_log.status = 'running'
            sync_log.started_at = datetime.utcnow()
            db.session.add(sync_log)
            db.session.commit()
            
            try:
                logger.info(f"Sincronizando repositórios públicos para: {username}")
                
                # Get public repositories
                repositories = self._get_public_repositories(username)
                
                if not repositories:
                    self._update_sync_log(sync_log, 'success', None, 0)
                    return True, f"Nenhum repositório público encontrado para {username}", 0
                
                synced_count = 0
                errors = []
                
                for repo_data in repositories:
                    try:
                        if self._sync_repository(username, repo_data):
                            synced_count += 1
                    except Exception as e:
                        error_msg = f"Erro ao sincronizar {repo_data.get('name', 'unknown')}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
                # Update sync log
                if errors and synced_count == 0:
                    status = 'error'
                    message = f"Falha ao sincronizar repositórios: {'; '.join(errors[:3])}"
                elif errors:
                    status = 'partial'
                    message = f"Sincronizados {synced_count}/{len(repositories)} repositórios"
                else:
                    status = 'success'
                    message = f"Sincronizados {synced_count} repositórios com sucesso"
                
                self._update_sync_log(sync_log, status, message if errors else None, synced_count)
                
                logger.info(f"Sincronização concluída: {message}")
                return status != 'error', message, synced_count
                
            except Exception as e:
                error_msg = f"Erro durante sincronização: {str(e)}"
                self._update_sync_log(sync_log, 'error', error_msg, 0)
                logger.error(error_msg)
                return False, error_msg, 0
    
    def _get_public_repositories(self, username: str) -> list:
        """Get public repositories for a user"""
        repositories = []
        page = 1
        per_page = 100
        
        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/users/{username}/repos",
                    params={
                        'per_page': per_page,
                        'page': page,
                        'sort': 'updated',
                        'direction': 'desc',
                        'type': 'public'  # Only public repositories
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
                
            except requests.RequestException as e:
                logger.error(f"Erro ao buscar repositórios: {e}")
                break
        
        logger.info(f"Encontrados {len(repositories)} repositórios públicos")
        return repositories
    
    def _sync_repository(self, username: str, repo_data: dict) -> bool:
        """Sync a single repository"""
        try:
            github_id = repo_data['id']
            
            # Check if repository exists
            existing_repo = GitHubRepository.query.filter_by(github_id=github_id).first()
            
            if existing_repo:
                repository = existing_repo
                logger.debug(f"Atualizando repositório: {repo_data['name']}")
            else:
                repository = GitHubRepository()
                repository.github_id = github_id
                db.session.add(repository)
                logger.debug(f"Criando repositório: {repo_data['name']}")
            
            # Update repository fields
            self._update_repository_from_data(repository, repo_data)
            
            # Get languages
            self._sync_repository_languages(repository, username, repo_data['name'])
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao sincronizar repositório {repo_data.get('name', 'unknown')}: {e}")
            return False
    
    def _update_repository_from_data(self, repository: GitHubRepository, repo_data: dict):
        """Update repository with GitHub data"""
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
    
    def _sync_repository_languages(self, repository: GitHubRepository, owner: str, repo_name: str):
        """Get repository languages (public API)"""
        try:
            response = self.session.get(f"{self.base_url}/repos/{owner}/{repo_name}/languages")
            response.raise_for_status()
            languages_data = response.json()
            
            if not languages_data:
                return
            
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
            
        except Exception as e:
            logger.warning(f"Erro ao buscar linguagens para {repo_name}: {e}")
    
    def _update_sync_log(self, sync_log: GitHubSyncLog, status: str, error_message: str, repositories_synced: int):
        """Update sync log"""
        sync_log.status = status
        sync_log.error_message = error_message
        sync_log.repositories_synced = repositories_synced
        sync_log.completed_at = datetime.utcnow()
        db.session.commit()

def sync_user_public_repos(username: str):
    """Convenience function to sync public repos"""
    sync_service = PublicGitHubSync()
    return sync_service.sync_public_repositories(username)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python github_public_sync.py <username>")
        print("Exemplo: python github_public_sync.py octocat")
        sys.exit(1)
    
    username = sys.argv[1]
    success, message, count = sync_user_public_repos(username)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        sys.exit(1)
