
#!/usr/bin/env python3
"""
Automatic GitHub sync scheduler
"""
import os
import time
import threading
import logging
from datetime import datetime, timedelta

# Safe imports to avoid circular dependencies
try:
    from app import app, db
    from github_sync import GitHubSyncService
    from models import GitHubCredentials, GitHubSyncLog
except ImportError as e:
    print(f"Import error in auto_sync_scheduler: {e}")
    app = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAutoSync:
    """Automatic GitHub synchronization service"""
    
    def __init__(self, sync_interval_hours=6):
        self.sync_interval_hours = sync_interval_hours
        self.running = False
        self.sync_thread = None
    
    def start_auto_sync(self):
        """Start automatic synchronization in background"""
        if self.running:
            logger.info("Auto-sync já está rodando")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info(f"Auto-sync iniciado (intervalo: {self.sync_interval_hours}h)")
    
    def stop_auto_sync(self):
        """Stop automatic synchronization"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("Auto-sync parado")
    
    def _sync_loop(self):
        """Main sync loop"""
        # Run initial sync on startup
        self._run_sync()
        
        # Continue with scheduled syncs
        while self.running:
            try:
                time.sleep(self.sync_interval_hours * 3600)  # Convert hours to seconds
                if self.running:
                    self._run_sync()
            except Exception as e:
                logger.error(f"Erro no loop de sincronização: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _run_sync(self):
        """Run a single sync operation"""
        try:
            with app.app_context():
                credentials = GitHubCredentials.query.filter_by(is_active=True).first()
                if not credentials:
                    logger.warning("Nenhuma credencial GitHub encontrada para auto-sync")
                    return
                
                username = credentials.username
                
                # Check last sync time to avoid too frequent syncs
                last_sync = GitHubSyncLog.query.filter_by(
                    username=username
                ).order_by(GitHubSyncLog.started_at.desc()).first()
                
                if last_sync and last_sync.started_at:
                    time_since_last = datetime.utcnow() - last_sync.started_at
                    if time_since_last < timedelta(hours=1):
                        logger.info("Pulando sync - muito recente")
                        return
                
                logger.info(f"Executando auto-sync para {username}")
                
                sync_service = GitHubSyncService()
                success, message, repos_synced = sync_service.sync_user_repositories(username)
                
                if success:
                    logger.info(f"Auto-sync concluído: {repos_synced} repositórios")
                else:
                    logger.error(f"Auto-sync falhou: {message}")
                    
        except Exception as e:
            logger.error(f"Erro durante auto-sync: {e}")

# Global instance
auto_sync = GitHubAutoSync()

def start_background_sync():
    """Start background synchronization service"""
    if not app:
        logger.error("App não disponível para auto-sync")
        return False
        
    # Only start if we have GitHub credentials or token
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            # Start sync even if no credentials in DB yet
            auto_sync.start_auto_sync()
            return True
            
        with app.app_context():
            if GitHubCredentials.query.filter_by(is_active=True).first():
                auto_sync.start_auto_sync()
                return True
    except Exception as e:
        logger.error(f"Erro ao iniciar auto-sync: {e}")
    return False

def stop_background_sync():
    """Stop background synchronization service"""
    auto_sync.stop_auto_sync()

if __name__ == "__main__":
    print("Iniciando serviço de auto-sincronização...")
    if start_background_sync():
        print("✅ Serviço iniciado com sucesso!")
        try:
            while True:
                time.sleep(60)  # Keep the script running
        except KeyboardInterrupt:
            print("\n🛑 Parando serviço...")
            stop_background_sync()
            print("✅ Serviço parado")
    else:
        print("❌ Falha ao iniciar serviço - configure as credenciais primeiro")
