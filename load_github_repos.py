#!/usr/bin/env python3
"""
Script to load GitHub repositories using stored encrypted credentials
"""
import sys
from app import app, db
from github_sync import GitHubSyncService
from models import GitHubCredentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_repositories():
    """Load GitHub repositories from the authenticated user"""
    with app.app_context():
        try:
            # Get stored credentials
            credentials = GitHubCredentials.query.filter_by(is_active=True).first()
            if not credentials:
                logger.error("No GitHub credentials found in database")
                return False
            
            username = credentials.username
            logger.info(f"Loading repositories for user: {username}")
            
            # Initialize sync service
            sync_service = GitHubSyncService()
            
            # Validate connection first
            if not sync_service.client.validate_connection():
                logger.error("GitHub connection validation failed")
                return False
            
            # Sync repositories
            success, message, repos_synced = sync_service.sync_user_repositories(username)
            
            if success:
                logger.info(f"Successfully synced {repos_synced} repositories")
                logger.info(f"Message: {message}")
                return True
            else:
                logger.error(f"Failed to sync repositories: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading repositories: {e}")
            return False

if __name__ == "__main__":
    success = load_repositories()
    sys.exit(0 if success else 1)