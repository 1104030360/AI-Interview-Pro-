"""
Cryptography utilities for sensitive data encryption

Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256)
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_fernet_instance = None

# Read encryption key from environment
AI_SETTINGS_ENCRYPTION_KEY = os.getenv('AI_SETTINGS_ENCRYPTION_KEY')


def get_fernet():
    """
    Get or create Fernet instance (singleton)

    Returns:
        Fernet: Encryption instance

    Raises:
        RuntimeError: If encryption key not configured in production
    """
    global _fernet_instance

    if _fernet_instance is None:
        key = os.getenv('AI_SETTINGS_ENCRYPTION_KEY')
        env = os.getenv('FLASK_ENV', 'development')

        if not key:
            if env == 'production':
                raise RuntimeError(
                    "AI_SETTINGS_ENCRYPTION_KEY must be set in production environment. "
                    "Generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
                )
            # In development/test mode, use a default key (NOT for production)
            logger.warning(
                "AI_SETTINGS_ENCRYPTION_KEY not set - using development key. "
                "DO NOT use in production!"
            )
            key = "DEVELOPMENT_KEY_DO_NOT_USE_IN_PRODUCTION_32B="

        try:
            from cryptography.fernet import Fernet
            # Fernet key must be 32 url-safe base64-encoded bytes
            # Try to use the key directly, or generate from a password
            try:
                _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
            except Exception:
                # If key is not valid Fernet format, derive a key from it
                import base64
                import hashlib
                # Create a valid 32-byte key from the provided string
                derived = hashlib.sha256(key.encode()).digest()
                key_b64 = base64.urlsafe_b64encode(derived)
                _fernet_instance = Fernet(key_b64)
        except ImportError:
            logger.error("cryptography package not installed")
            raise RuntimeError("cryptography package required for encryption")

    return _fernet_instance


def encrypt_api_key(plaintext: Optional[str]) -> str:
    """
    Encrypt API key for storage

    Args:
        plaintext: Raw API key string

    Returns:
        str: Base64-encoded ciphertext (Fernet format starts with 'gAAAAA')
    """
    if not plaintext:
        return ''

    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError("Failed to encrypt API key")


def decrypt_api_key(ciphertext: Optional[str]) -> str:
    """
    Decrypt stored API key

    Args:
        ciphertext: Base64-encoded encrypted string

    Returns:
        str: Original API key, or empty string if decryption fails
    """
    if not ciphertext:
        return ''

    # Check if the value is already plaintext (legacy data)
    # Fernet tokens start with 'gAAAAA'
    if not ciphertext.startswith('gAAAAA'):
        logger.debug("Value appears to be unencrypted, returning as-is")
        return ciphertext

    try:
        from cryptography.fernet import InvalidToken
        fernet = get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode())
        return decrypted.decode()
    except ImportError:
        logger.error("cryptography package not installed")
        return ''
    except Exception as e:
        # InvalidToken or other errors - return empty string
        logger.warning(f"Decryption failed (key may have changed): {e}")
        return ''


def validate_encryption_key() -> bool:
    """
    Validate that encryption key is configured and valid

    Returns:
        bool: True if key is valid

    Raises:
        RuntimeError: If key is missing in production or invalid
    """
    key = os.getenv('AI_SETTINGS_ENCRYPTION_KEY')
    env = os.getenv('FLASK_ENV', 'development')

    if not key:
        if env == 'production':
            raise RuntimeError(
                "AI_SETTINGS_ENCRYPTION_KEY must be set in production environment"
            )
        logger.warning("AI_SETTINGS_ENCRYPTION_KEY not set - using development mode")
        return True  # Allow development mode

    try:
        from cryptography.fernet import Fernet
        # Try to create Fernet instance to validate key
        Fernet(key.encode())
        return True
    except Exception as e:
        raise RuntimeError(f"Invalid AI_SETTINGS_ENCRYPTION_KEY: {e}")
