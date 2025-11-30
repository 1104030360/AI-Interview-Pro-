"""
Tests for crypto utilities
"""
import pytest
import os


class TestCrypto:
    """Test encryption/decryption functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test encryption key"""
        # Use a fixed test key
        os.environ['AI_SETTINGS_ENCRYPTION_KEY'] = 'test-encryption-key-for-unit-tests'

        # Reset singleton
        import backend.utils.crypto as crypto_module
        crypto_module._fernet_instance = None

        yield

        # Cleanup
        if 'AI_SETTINGS_ENCRYPTION_KEY' in os.environ:
            del os.environ['AI_SETTINGS_ENCRYPTION_KEY']
        crypto_module._fernet_instance = None

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly"""
        from backend.utils.crypto import encrypt_api_key, decrypt_api_key

        original = "sk-test-api-key-12345"
        encrypted = encrypt_api_key(original)
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == original
        assert encrypted != original
        assert encrypted.startswith('gAAAAA')  # Fernet format

    def test_encrypt_different_keys_produce_different_ciphertexts(self):
        """Test that encrypting the same value produces different ciphertexts"""
        from backend.utils.crypto import encrypt_api_key

        original = "sk-test-api-key"
        encrypted1 = encrypt_api_key(original)
        encrypted2 = encrypt_api_key(original)

        # Fernet includes timestamp and random IV, so ciphertexts should differ
        assert encrypted1 != encrypted2

    def test_encrypt_empty_string(self):
        """Test that empty strings are handled correctly"""
        from backend.utils.crypto import encrypt_api_key

        assert encrypt_api_key('') == ''

    def test_encrypt_none(self):
        """Test that None is handled correctly"""
        from backend.utils.crypto import encrypt_api_key

        assert encrypt_api_key(None) == ''

    def test_decrypt_empty_string(self):
        """Test that empty strings decrypt to empty strings"""
        from backend.utils.crypto import decrypt_api_key

        assert decrypt_api_key('') == ''

    def test_decrypt_none(self):
        """Test that None decrypts to empty string"""
        from backend.utils.crypto import decrypt_api_key

        assert decrypt_api_key(None) == ''

    def test_decrypt_plaintext_passthrough(self):
        """Test that plaintext values (legacy data) pass through unchanged"""
        from backend.utils.crypto import decrypt_api_key

        # Plaintext that doesn't start with gAAAAA should pass through
        plaintext = "sk-old-unencrypted-key"
        result = decrypt_api_key(plaintext)

        assert result == plaintext

    def test_decrypt_invalid_token(self):
        """Test that invalid tokens return empty string"""
        from backend.utils.crypto import decrypt_api_key

        # This looks like Fernet format but is invalid
        invalid = "gAAAAACinvalid-base64-data"
        result = decrypt_api_key(invalid)

        # Should return empty string, not raise exception
        assert result == ''

    def test_long_api_key(self):
        """Test encryption of long API keys"""
        from backend.utils.crypto import encrypt_api_key, decrypt_api_key

        # OpenAI keys are typically around 50 chars
        long_key = "sk-" + "a" * 100

        encrypted = encrypt_api_key(long_key)
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == long_key

    def test_special_characters_in_key(self):
        """Test encryption of keys with special characters"""
        from backend.utils.crypto import encrypt_api_key, decrypt_api_key

        special_key = "sk-test_key-with/special+chars="

        encrypted = encrypt_api_key(special_key)
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == special_key

    def test_unicode_in_key(self):
        """Test encryption of keys with unicode characters"""
        from backend.utils.crypto import encrypt_api_key, decrypt_api_key

        unicode_key = "sk-test-密鑰-🔑"

        encrypted = encrypt_api_key(unicode_key)
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == unicode_key


class TestCryptoIntegration:
    """Integration tests for crypto with settings service"""

    @pytest.fixture(scope='class')
    def test_app(self):
        """Create application for testing"""
        import sys
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

        from backend.app import create_app
        from backend.config_backend import Config
        from backend.database import db

        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            JWT_SECRET_KEY = 'test-secret-key'

        app = create_app(TestConfig)

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        os.environ['AI_SETTINGS_ENCRYPTION_KEY'] = 'integration-test-key'

        import backend.utils.crypto as crypto_module
        crypto_module._fernet_instance = None

        yield

        if 'AI_SETTINGS_ENCRYPTION_KEY' in os.environ:
            del os.environ['AI_SETTINGS_ENCRYPTION_KEY']
        crypto_module._fernet_instance = None

    def test_settings_service_encrypts_api_key(self, test_app):
        """Test that SettingsService encrypts API keys when storing"""
        from backend.services.settings_service import SettingsService
        from backend.services.auth_service import AuthService
        from backend.models.user_settings import UserSettings

        with test_app.app_context():
            # Create test user
            user = AuthService.register_user(
                email='crypto_test@example.com',
                password='test123',
                name='Crypto Test'
            )

            # Update settings with API key
            SettingsService.update_user_settings(user.id, {
                'ai': {
                    'apiKey': 'sk-secret-api-key-12345'
                }
            })

            # Check database directly
            settings = UserSettings.query.filter_by(user_id=user.id).first()

            # Should be encrypted in database
            assert settings.ai_api_key_encrypted is not None
            assert settings.ai_api_key_encrypted.startswith('gAAAAA')
            assert settings.ai_api_key_encrypted != 'sk-secret-api-key-12345'

    def test_settings_service_decrypts_api_key(self, test_app):
        """Test that SettingsService decrypts API keys when reading"""
        from backend.services.settings_service import SettingsService
        from backend.services.auth_service import AuthService

        with test_app.app_context():
            # Create test user
            user = AuthService.register_user(
                email='crypto_test2@example.com',
                password='test123',
                name='Crypto Test 2'
            )

            original_key = 'sk-my-secret-key-67890'

            # Store encrypted
            SettingsService.update_user_settings(user.id, {
                'ai': {
                    'apiKey': original_key
                }
            })

            # Read back
            settings = SettingsService.get_user_settings(user.id)

            # Should be decrypted
            assert settings['ai']['apiKey'] == original_key
