#!/usr/bin/env python3
"""
Script para configurar o token GitHub para sincronização automática
"""
import os
import sys
from app import app, db
from models import GitHubCredentials
from crypto_utils import encrypt_data

def setup_github_token():
    """Configure GitHub token for automatic synchronization"""

    # Get token from environment variable
    github_token = os.environ.get('GITHUB_TOKEN')

    if not github_token:
        print("INFO: GITHUB_TOKEN não encontrado nas variáveis de ambiente")
        print("INFO: Configure o token em Secrets no Replit:")
        print("INFO: 1. Vá para a aba Secrets (🔒)")
        print("INFO: 2. Adicione: GITHUB_TOKEN = seu_token_github")
        print("INFO: Pule esta configuração se não quiser sincronização automática")
        return True  # Return True to not block the system

    try:
        with app.app_context():
            # Check if credentials already exist
            existing_creds = GitHubCredentials.query.filter_by(is_active=True).first()

            if existing_creds:
                print("INFO: Credenciais GitHub já configuradas, atualizando...")
                # Update existing credentials
                existing_creds.encrypted_token = encrypt_data(github_token)
                existing_creds.username = 'cDorth'  # Update with your GitHub username
            else:
                print("INFO: Configurando novas credenciais GitHub...")
                # Create new credentials
                credentials = GitHubCredentials()
                credentials.username = 'cDorth'  # Replace with your GitHub username
                credentials.encrypted_token = encrypt_data(github_token)
                credentials.is_active = True
                db.session.add(credentials)

            db.session.commit()
            print("✅ GitHub token configurado com sucesso!")
            print("✅ Sistema de sincronização automática ativo")

            # Test the connection
            from github_sync import GitHubSyncService
            sync_service = GitHubSyncService()

            if sync_service.client.validate_connection():
                print("✅ Conexão com GitHub validada com sucesso!")
                return True
            else:
                print("⚠️  Falha na validação da conexão com GitHub")
                return True  # Don't block the system

    except Exception as e:
        print(f"⚠️  Aviso durante configuração: {e}")
        return True  # Don't block the system

if __name__ == "__main__":
    success = setup_github_token()
    print("\n✅ Sistema inicializado. Configure GITHUB_TOKEN para sincronização automática.")
    sys.exit(0)