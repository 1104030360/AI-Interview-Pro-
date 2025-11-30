"""Encrypt existing API keys in user_settings

Revision ID: 20251130_encrypt_keys
Revises: 90552c584965
Create Date: 2025-11-30

This is a data migration script that encrypts any existing plaintext API keys
in the user_settings table. It detects plaintext keys (those not starting with
'gAAAAA' Fernet prefix) and encrypts them using the configured encryption key.

IMPORTANT: Before running this migration, ensure AI_SETTINGS_ENCRYPTION_KEY
environment variable is set. Generate a key with:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
import os
import logging

# revision identifiers, used by Alembic.
revision = '20251130_encrypt_keys'
down_revision = '90552c584965'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)


def is_fernet_ciphertext(value: str) -> bool:
    """Check if a string looks like Fernet ciphertext.

    Fernet tokens are URL-safe base64 and always start with 'gAAAAA'.
    """
    if not value or len(value) < 10:
        return False
    return value.startswith('gAAAAA')


def upgrade():
    """Encrypt all existing plaintext API keys."""
    # Get encryption key from environment
    encryption_key = os.environ.get('AI_SETTINGS_ENCRYPTION_KEY')

    if not encryption_key:
        logger.warning(
            "AI_SETTINGS_ENCRYPTION_KEY not set. "
            "Skipping API key encryption migration. "
            "Run this migration again after setting the environment variable."
        )
        return

    try:
        from cryptography.fernet import Fernet
        fernet = Fernet(encryption_key.encode())
    except Exception as e:
        logger.error(f"Failed to initialize Fernet with provided key: {e}")
        raise RuntimeError(
            "Invalid AI_SETTINGS_ENCRYPTION_KEY. "
            "Generate a valid key with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    # Get database connection
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Query all user_settings with non-empty API keys
        result = session.execute(
            sa.text("""
                SELECT id, ai_api_key_encrypted
                FROM user_settings
                WHERE ai_api_key_encrypted IS NOT NULL
                  AND ai_api_key_encrypted != ''
            """)
        )

        rows = result.fetchall()
        encrypted_count = 0
        skipped_count = 0

        for row in rows:
            settings_id = row[0]
            api_key = row[1]

            # Skip if already encrypted (Fernet format)
            if is_fernet_ciphertext(api_key):
                logger.info(f"Skipping settings {settings_id}: already encrypted")
                skipped_count += 1
                continue

            # Encrypt the plaintext key
            try:
                encrypted = fernet.encrypt(api_key.encode()).decode()
                session.execute(
                    sa.text("""
                        UPDATE user_settings
                        SET ai_api_key_encrypted = :encrypted
                        WHERE id = :id
                    """),
                    {"encrypted": encrypted, "id": settings_id}
                )
                encrypted_count += 1
                logger.info(f"Encrypted API key for settings {settings_id}")
            except Exception as e:
                logger.error(f"Failed to encrypt API key for settings {settings_id}: {e}")
                raise

        session.commit()
        logger.info(
            f"API key encryption migration complete. "
            f"Encrypted: {encrypted_count}, Skipped (already encrypted): {skipped_count}"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        session.close()


def downgrade():
    """Downgrade is not supported for security reasons.

    Decrypting API keys back to plaintext would be a security risk.
    If you need to revert this migration, restore from a database backup.
    """
    logger.warning(
        "Downgrade of API key encryption is not supported for security reasons. "
        "Restore from database backup if needed."
    )
    # Intentionally left empty - we cannot safely reverse encryption
    pass
