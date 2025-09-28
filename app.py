import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable must be set")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - PostgreSQL (integrated Replit database)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    # Create all tables if they don't exist
    db.create_all()
    
    # Superadmin seeding disabled for security
    
    # GitHub credentials configured for on-demand sync
    logging.info("GitHub sync system initialized")
    
    # Auto-configure GitHub credentials and sync repositories
    try:
        from crypto_utils import crypto_manager
        from github_client import GitHubClient
        from github_sync import GitHubSyncService
        
        # Check if GITHUB_TOKEN exists
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            logging.warning("="*80)
            logging.warning("GITHUB_TOKEN não configurado!")
            logging.warning("Para carregar automaticamente seus projetos GitHub:")
            logging.warning("1. Vá em Secrets (🔒) no painel lateral do Replit")
            logging.warning("2. Adicione: GITHUB_TOKEN = seu_token_github")
            logging.warning("3. Reinicie a aplicação")
            logging.warning("="*80)
        else:
            # Initialize GitHub client and sync repositories
            client = GitHubClient()
            
            # Validate and store credentials
            if client.validate_connection():
                # Get user info to store credentials
                user_info = client.get_authenticated_user()
                if user_info:
                    username = user_info.get('login')
                    
                    if username:  # Only proceed if username is not None
                        # Store encrypted credentials in database (if crypto available)
                        try:
                            if crypto_manager is not None:
                                client.store_github_credentials(username, github_token)
                                logging.info(f"GitHub credentials armazenadas para: {username}")
                            else:
                                logging.info(f"GitHub conectado para: {username} (sem criptografia)")
                        except Exception as e:
                            logging.warning(f"Aviso ao armazenar credenciais: {e}")
                        
                        # Perform initial sync of repositories
                        try:
                            sync_service = GitHubSyncService()
                            logging.info(f"Iniciando sincronização de repositórios para {username}...")
                            
                            success, message, repos_synced = sync_service.sync_user_repositories(username)
                            if success:
                                logging.info(f"✅ Sincronização concluída: {repos_synced} repositórios carregados")
                            else:
                                logging.warning(f"⚠️ Sincronização parcial: {message}")
                        except Exception as sync_error:
                            logging.error(f"Erro na sincronização: {sync_error}")
                        
                else:
                    logging.error("Não foi possível obter informações do usuário GitHub")
            else:
                logging.error("Token GitHub inválido - verifique suas permissões")
        
        # Start background sync (optional)
        try:
            from auto_sync_scheduler import start_background_sync
            if start_background_sync():
                logging.info("Sincronização automática em background ativada")
        except Exception as e:
            logging.debug(f"Background sync não iniciado: {e}")
            
    except Exception as e:
        logging.warning(f"GitHub setup error: {e}")
        logging.info("Sistema continuará sem sincronização GitHub")

# Import and initialize API routes
from api_routes import init_api_routes
init_api_routes(app)
