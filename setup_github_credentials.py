#!/usr/bin/env python3
"""
Script to setup GitHub credentials from environment variables
"""
import os
import sys
from app import app, db
from github_client import GitHubClient
from models import GitHubCredentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_credentials():
    """Setup GitHub credentials from environment"""
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
            client = GitHubClient()
            
            # Check if credentials already exist
            existing = GitHubCredentials.query.filter_by(is_active=True).first()
            if existing:
                logger.info("GitHub credentials already exist in database")
                return True
            
            # Initialize from environment
            success = client.initialize_credentials_from_env()
            if success:
                logger.info("GitHub credentials successfully migrated to database")
                return True
            else:
                logger.error("Failed to setup GitHub credentials")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up credentials: {e}")
            return False

if __name__ == "__main__":
    success = setup_credentials()
    sys.exit(0 if success else 1)