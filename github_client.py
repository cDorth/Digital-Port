import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import requests
from flask import current_app
from models import GitHubCredentials
from crypto_utils import crypto_manager
from app import db

logger = logging.getLogger(__name__)

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass

class GitHubClient:
    """
    GitHub API client using Replit's GitHub integration
    """
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self._access_token = None
        
    def _get_access_token(self) -> str:
        """
        Get the GitHub access token from encrypted storage or environment
        """
        if self._access_token:
            return self._access_token
            
        # First try to get from database (encrypted storage)
        try:
            if crypto_manager is not None:
                credentials = GitHubCredentials.query.filter_by(is_active=True).first()
                if credentials:
                    self._access_token = crypto_manager.decrypt(credentials.encrypted_token)
                    # Update last used time
                    credentials.last_used_at = datetime.utcnow()
                    db.session.commit()
                    return self._access_token
        except Exception as e:
            logger.warning(f"Failed to get token from database: {e}")
        
        # Fallback to environment variable (for initial setup)
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            self._access_token = github_token
            return github_token
            
        raise GitHubAPIError('GitHub access token not available. Please configure your GitHub credentials.')
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an authenticated request to the GitHub API
        """
        access_token = self._get_access_token()
        
        headers = kwargs.get('headers', {})
        headers.update({
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ReplicationPortfolio/1.0'
        })
        kwargs['headers'] = headers
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    reset_datetime = datetime.fromtimestamp(int(reset_time), tz=timezone.utc)
                    raise GitHubAPIError(f'Rate limit exceeded. Resets at {reset_datetime}')
                else:
                    raise GitHubAPIError('Rate limit exceeded')
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise GitHubAPIError(f'GitHub API request failed: {e}')
    
    def get_user_repositories(self, username: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get all public repositories for a user
        """
        repositories = []
        page = 1
        
        while True:
            try:
                response = self._make_request(
                    'GET',
                    f'/users/{username}/repos',
                    params={
                        'per_page': per_page,
                        'page': page,
                        'sort': 'updated',
                        'direction': 'desc'
                    }
                )
                
                if not response:
                    break
                
                repositories.extend(response)
                
                # If we got fewer than requested, we're on the last page
                if len(response) < per_page:
                    break
                
                page += 1
                
            except GitHubAPIError as e:
                logger.error(f"Error fetching repositories for {username}: {e}")
                raise
        
        logger.info(f"Fetched {len(repositories)} repositories for user {username}")
        return repositories
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get programming languages used in a repository with byte counts
        """
        try:
            response = self._make_request('GET', f'/repos/{owner}/{repo}/languages')
            return response
        except GitHubAPIError as e:
            logger.warning(f"Error fetching languages for {owner}/{repo}: {e}")
            return {}
    
    def get_repository_details(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific repository
        """
        try:
            response = self._make_request('GET', f'/repos/{owner}/{repo}')
            return response
        except GitHubAPIError as e:
            logger.warning(f"Error fetching details for {owner}/{repo}: {e}")
            return None

    def get_authenticated_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently authenticated GitHub user
        """
        try:
            response = self._make_request('GET', '/user')
            return response
        except GitHubAPIError:
            return None

    def validate_connection(self) -> bool:
        """
        Test if the GitHub connection is working
        """
        try:
            user = self.get_authenticated_user()
            return bool(user and user.get('login'))
        except GitHubAPIError:
            return False
    
    def store_github_credentials(self, username: str, token: str) -> bool:
        """
        Store GitHub credentials encrypted in the database
        """
        try:
            # Deactivate any existing credentials
            existing = GitHubCredentials.query.filter_by(username=username).first()
            if existing:
                existing.is_active = False
            
            # Create new encrypted credentials
            if crypto_manager is None:
                logger.error("Cannot store credentials - encryption not available")
                return False
            encrypted_token = crypto_manager.encrypt(token)
            credentials = GitHubCredentials(
                username=username,
                encrypted_token=encrypted_token,
                is_active=True
            )
            
            db.session.add(credentials)
            db.session.commit()
            
            logger.info(f"GitHub credentials stored for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store GitHub credentials: {e}")
            db.session.rollback()
            return False
    
    def initialize_credentials_from_env(self) -> bool:
        """
        Initialize credentials from environment variables and store in database
        """
        try:
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                logger.warning("No GITHUB_TOKEN found in environment")
                return False
            
            # Validate token by getting user info
            temp_token = self._access_token
            self._access_token = github_token
            
            user_info = self.get_authenticated_user()
            if not user_info:
                self._access_token = temp_token
                logger.error("Invalid GitHub token")
                return False
            
            username = user_info.get('login')
            if not username:
                self._access_token = temp_token
                logger.error("Could not get username from GitHub API")
                return False
            
            # Store credentials in database
            success = self.store_github_credentials(username, github_token)
            
            self._access_token = temp_token
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize credentials from environment: {e}")
            return False