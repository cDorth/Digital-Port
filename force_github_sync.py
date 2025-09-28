
#!/usr/bin/env python3
"""
Script para forçar sincronização do GitHub
"""
import os
import sys
import logging
from app import app, db
from github_client import GitHubClient
from github_sync import GitHubSyncService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_sync():
    """Força a sincronização dos repositórios GitHub"""
    with app.app_context():
        try:
            # Verificar se há token GitHub
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                logger.error("GITHUB_TOKEN não encontrado nas variáveis de ambiente")
                logger.info("Configure o token em Secrets e tente novamente")
                return False
            
            # Inicializar cliente GitHub
            client = GitHubClient()
            
            # Validar conexão
            if not client.validate_connection():
                logger.error("Falha na validação da conexão GitHub")
                return False
            
            # Obter informações do usuário
            user_info = client.get_authenticated_user()
            if not user_info:
                logger.error("Não foi possível obter informações do usuário")
                return False
            
            username = user_info.get('login')
            logger.info(f"Usuário GitHub conectado: {username}")
            
            # Inicializar serviço de sincronização
            sync_service = GitHubSyncService()
            
            # Executar sincronização
            logger.info("Iniciando sincronização forçada...")
            success, message, repos_synced = sync_service.sync_user_repositories(username)
            
            if success:
                logger.info(f"✅ Sincronização bem-sucedida!")
                logger.info(f"📁 Repositórios sincronizados: {repos_synced}")
                logger.info(f"💬 Mensagem: {message}")
                
                # Mostrar alguns repositórios sincronizados
                from models import GitHubRepository
                recent_repos = GitHubRepository.query.order_by(
                    GitHubRepository.last_sync_at.desc()
                ).limit(5).all()
                
                if recent_repos:
                    logger.info("📋 Últimos repositórios sincronizados:")
                    for repo in recent_repos:
                        logger.info(f"  - {repo.name} ({repo.language or 'N/A'})")
                
                return True
            else:
                logger.error(f"❌ Falha na sincronização: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante sincronização forçada: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Forçando sincronização do GitHub...")
    success = force_sync()
    
    if success:
        print("\n✅ Sincronização concluída com sucesso!")
        print("🌐 Acesse /projects para ver os repositórios")
    else:
        print("\n❌ Falha na sincronização")
        print("🔧 Verifique os logs acima para detalhes")
    
    sys.exit(0 if success else 1)
