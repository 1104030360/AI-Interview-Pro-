"""
Unit tests for SettingsService

Tests user settings management functionality:
- Get user settings (with auto-creation)
- Update user settings
- Default settings creation
"""
import pytest
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.user_settings import UserSettings
from backend.services.settings_service import SettingsService
import uuid


@pytest.fixture(scope='module')
def app():
    """Create application for testing"""
    from backend.config_backend import Config

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


@pytest.fixture(scope='function')
def test_user(app):
    """Create test user"""
    import bcrypt

    with app.app_context():
        password_hash = bcrypt.hashpw(
            'password123'.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        user = User(
            id=str(uuid.uuid4()),
            email='test@example.com',
            name='Test User',
            password_hash=password_hash
        )
        db.session.add(user)
        db.session.commit()

        user_id = user.id
        yield user_id

        # Cleanup
        User.query.filter_by(id=user_id).delete()
        UserSettings.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class TestSettingsService:
    """Test SettingsService methods"""

    def test_get_user_settings_creates_default(self, app, test_user):
        """Test get settings creates default if not exist"""
        with app.app_context():
            # Get settings (should create default)
            settings = SettingsService.get_user_settings(test_user)

            assert settings is not None
            assert 'profile' in settings
            assert 'ai' in settings
            assert 'prompts' in settings

            # Check defaults
            assert settings['ai']['provider'] == 'ollama'
            assert settings['ai']['model'] == 'llama3:latest'
            assert settings['profile']['language'] == 'en'

    def test_get_existing_settings(self, app, test_user):
        """Test get existing settings"""
        with app.app_context():
            # Create settings manually
            settings_obj = UserSettings(
                user_id=test_user,
                display_name='Custom Name',
                job_role='Backend Engineer',
                ai_provider='openai',
                ai_model='gpt-4'
            )
            db.session.add(settings_obj)
            db.session.commit()

            # Get settings
            settings = SettingsService.get_user_settings(test_user)

            assert settings['profile']['name'] == 'Custom Name'
            assert settings['profile']['role'] == 'Backend Engineer'
            assert settings['ai']['provider'] == 'openai'
            assert settings['ai']['model'] == 'gpt-4'

    def test_update_profile_settings(self, app, test_user):
        """Test update profile settings"""
        with app.app_context():
            # Update profile
            update_data = {
                'profile': {
                    'name': 'Updated Name',
                    'role': 'Senior Engineer',
                    'language': 'zh-TW'
                }
            }

            result = SettingsService.update_user_settings(test_user, update_data)

            assert result['profile']['name'] == 'Updated Name'
            assert result['profile']['role'] == 'Senior Engineer'
            assert result['profile']['language'] == 'zh-TW'

            # Verify persistence
            settings = SettingsService.get_user_settings(test_user)
            assert settings['profile']['name'] == 'Updated Name'

    def test_update_ai_config(self, app, test_user):
        """Test update AI configuration"""
        with app.app_context():
            # Update AI config
            update_data = {
                'ai': {
                    'provider': 'openai',
                    'apiKey': 'sk-test-key-123',
                    'model': 'gpt-4'
                }
            }

            result = SettingsService.update_user_settings(test_user, update_data)

            assert result['ai']['provider'] == 'openai'
            assert result['ai']['apiKey'] == 'sk-test-key-123'
            assert result['ai']['model'] == 'gpt-4'

    def test_update_prompts(self, app, test_user):
        """Test update custom prompts"""
        with app.app_context():
            # Update prompts
            update_data = {
                'prompts': {
                    'global': 'Custom global prompt',
                    'interviewSuggestions': 'Custom interview prompt',
                    'coachChat': 'Custom coach prompt'
                }
            }

            result = SettingsService.update_user_settings(test_user, update_data)

            assert result['prompts']['global'] == 'Custom global prompt'
            assert result['prompts']['interviewSuggestions'] == 'Custom interview prompt'
            assert result['prompts']['coachChat'] == 'Custom coach prompt'

    def test_update_invalid_provider(self, app, test_user):
        """Test update with invalid AI provider"""
        with app.app_context():
            update_data = {
                'ai': {
                    'provider': 'invalid-provider'
                }
            }

            with pytest.raises(ValueError, match='Unsupported AI provider'):
                SettingsService.update_user_settings(test_user, update_data)

    def test_partial_update(self, app, test_user):
        """Test partial settings update"""
        with app.app_context():
            # Create initial settings
            SettingsService.update_user_settings(test_user, {
                'profile': {'name': 'Initial Name'},
                'ai': {'provider': 'ollama', 'model': 'llama3:latest'}
            })

            # Partial update (only change name)
            update_data = {
                'profile': {'name': 'New Name'}
            }

            result = SettingsService.update_user_settings(test_user, update_data)

            # Name should be updated, provider should remain
            assert result['profile']['name'] == 'New Name'
            assert result['ai']['provider'] == 'ollama'
            assert result['ai']['model'] == 'llama3:latest'
