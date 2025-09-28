
#!/usr/bin/env python3
"""
Setup automatic GitHub synchronization without manual login
"""
import os
import sys
import logging
from app import app, db
from github_sync import GitHubSyncService
from models import GitHubCredentials
from crypto_utils import crypto_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_github_token():
    """
    Configure GitHub token for automatic sync
    
    Para usar este script:
    1. Vá para https://github.com/settings/tokens
    2. Clique em "Generate new token (classic)"
    3. Selecione as permissões: repo, user:read
    4. Configure o token como variável de ambiente GITHUB_TOKEN
    """
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("\n" + "="*60)
        print("CONFIGURAÇÃO DO TOKEN GITHUB")
        print("="*60)
        print("1. Acesse: https://github.com/settings/tokens")
        print("2. Clique em 'Generate new token (classic)'")
        print("3. Dê um nome para o token (ex: 'Portfolio Sync')")
        print("4. Selecione as permissões:")
        print("   - repo (acesso completo aos repositórios)")
        print("   - user:read (ler informações do usuário)")
        print("5. Clique em 'Generate token'")
        print("6. Configure o token nas variáveis de ambiente do Replit")
        print("   - Vá em Secrets (🔒) no painel lateral")
        print("   - Adicione: GITHUB_TOKEN = seu_token_aqui")
        print("="*60)
        return False
    
    try:
        with app.app_context():
            # Test the token
            sync_service = GitHubSyncService()
            
            # Temporarily set the token for testing
            sync_service.client._access_token = github_token
            
            # Get user info to validate token
            user_info = sync_service.client.get_authenticated_user()
            if not user_info:
                logger.error("Token inválido ou sem permissões adequadas")
                return False
            
            username = user_info.get('login')
            logger.info(f"Token validado para usuário: {username}")
            
            # Store credentials in database
            existing = GitHubCredentials.query.filter_by(username=username).first()
            if existing:
                existing.is_active = False
            
            if crypto_manager is None:
                logger.error("Cannot store credentials - encryption not available")
                return False
            encrypted_token = crypto_manager.encrypt(github_token)
            credentials = GitHubCredentials(
                username=username,
                encrypted_token=encrypted_token,
                is_active=True
            )
            
            db.session.add(credentials)
            db.session.commit()
            
            logger.info(f"Credenciais armazenadas para {username}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao configurar token: {e}")
        return False

def run_initial_sync():
    """Run initial GitHub sync"""
    try:
        with app.app_context():
            credentials = GitHubCredentials.query.filter_by(is_active=True).first()
            if not credentials:
                logger.error("Nenhuma credencial encontrada")
                return False
            
            username = credentials.username
            sync_service = GitHubSyncService()
            
            logger.info(f"Iniciando sincronização para {username}")
            success, message, repos_synced = sync_service.sync_user_repositories(username)
            
            if success:
                logger.info(f"Sincronização concluída: {repos_synced} repositórios")
                return True
            else:
                logger.error(f"Falha na sincronização: {message}")
                return False
                
    except Exception as e:
        logger.error(f"Erro durante sincronização: {e}")
        return False

if __name__ == "__main__":
    print("Configurando sincronização automática do GitHub...")
    
    if setup_github_token():
        print("✅ Token configurado com sucesso!")
        
        if run_initial_sync():
            print("✅ Sincronização inicial concluída!")
            print("\nPróximos passos:")
            print("1. Os repositórios serão sincronizados automaticamente")
            print("2. Configure um cron job para sincronização periódica")
            print("3. Acesse /admin/github-sync para gerenciar a sincronização")
        else:
            print("❌ Falha na sincronização inicial")
    else:
        print("❌ Falha na configuração do token")
        sys.exit(1)
