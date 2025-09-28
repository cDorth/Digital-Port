import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class CryptoManager:
    """
    Manages encryption and decryption of sensitive data
    """
    
    def __init__(self):
        self._cipher = None
        self._initialize_cipher()
    
    def _initialize_cipher(self):
        """Initialize the cipher with the encryption key from environment"""
        try:
            encryption_key = os.environ.get('ENCRYPTION_KEY')
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY environment variable not found")
            
            # Use PBKDF2 to derive a key from the environment variable
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'portfolio_github_salt',  # Static salt for consistency
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
            self._cipher = Fernet(key)
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption cipher: {e}")
            raise
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string and return base64 encoded result
        """
        try:
            if not data:
                return ""
            
            encrypted = self._cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt base64 encoded encrypted data and return the original string
        """
        try:
            if not encrypted_data:
                return ""
            
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise

# Global instance - conditionally initialized
crypto_manager = None

def get_crypto_manager():
    """Get crypto manager instance, creating it if needed and possible"""
    global crypto_manager
    if crypto_manager is None:
        try:
            crypto_manager = CryptoManager()
        except ValueError as e:
            logger.warning(f"Crypto manager unavailable: {e}")
            return None
    return crypto_manager

# Try to initialize immediately, but don't fail if not possible
try:
    crypto_manager = CryptoManager()
except ValueError:
    logger.info("Crypto utilities disabled - ENCRYPTION_KEY not provided")
    crypto_manager = None