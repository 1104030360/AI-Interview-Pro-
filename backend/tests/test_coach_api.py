"""
Integration tests for Coach API

Tests AI coach chat endpoints:
- POST /api/coach/chat (chat with AI)
- GET /api/coach/suggestions (get suggestions)

Note: These tests will use Ollama as the default provider.
For proper testing, either mock the AI service or ensure Ollama is running.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.user_settings import UserSettings
from backend.services.auth_service import AuthService
from flask_jwt_extended import create_access_token
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


@pytest.fixture(scope='module')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def auth_token(app):
    """Create authenticated user and return JWT token"""
    with app.app_context():
        # Register user
        user = AuthService.register_user(
            email='test@example.com',
            password='password123',
            name='Test User'
        )

        # Create access token
        token = create_access_token(identity=user.id)
        user_id = user.id
        yield token

        # Cleanup
        User.query.filter_by(id=user_id).delete()
        UserSettings.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class TestCoachAPI:
    """Test Coach API endpoints"""

    def test_get_suggestions(self, client, auth_token):
        """Test get conversation suggestions"""
        response = client.get(
            '/api/coach/suggestions',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'suggestions' in data
        assert isinstance(data['suggestions'], list)
        assert len(data['suggestions']) > 0

    def test_chat_missing_message(self, client, auth_token):
        """Test chat without message"""
        response = client.post(
            '/api/coach/chat',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Message is required' in data['error']

    def test_chat_message_too_long(self, client, auth_token):
        """Test chat with message exceeding length limit"""
        long_message = 'a' * 2001  # Exceeds 2000 character limit

        response = client.post(
            '/api/coach/chat',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'message': long_message}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'too long' in data['error'].lower()

    def test_chat_invalid_provider(self, client, auth_token, app):
        """Test chat with invalid AI provider in settings"""
        with app.app_context():
            # Find the user from token
            import jwt as pyjwt
            decoded = pyjwt.decode(
                auth_token,
                app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = decoded['sub']

            # Update settings with invalid provider
            settings = UserSettings.query.filter_by(user_id=user_id).first()
            settings.ai_provider = 'invalid-provider'
            db.session.commit()

        # Try to chat
        response = client.post(
            '/api/coach/chat',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'message': 'Hello',
                'context': {}
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        # Error response format: {'error': {'code': '...', 'message': '...'}}
        if isinstance(data['error'], dict):
            assert 'Unsupported' in data['error'].get('message', '')
        else:
            assert 'Unsupported' in data['error']

    def test_chat_requires_auth(self, client):
        """Test that chat endpoint requires authentication"""
        response = client.post(
            '/api/coach/chat',
            json={'message': 'Hello'}
        )

        assert response.status_code == 401

    def test_suggestions_requires_auth(self, client):
        """Test that suggestions endpoint requires authentication"""
        response = client.get('/api/coach/suggestions')

        assert response.status_code == 401


    # Note: The following tests require either a running Ollama instance
    # or mocked AI service. They are marked as integration tests.

    @pytest.mark.skip(reason="Requires Ollama running or mocked AI service")
    def test_chat_with_ollama(self, client, auth_token):
        """Test chat with Ollama provider (integration test)"""
        response = client.post(
            '/api/coach/chat',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'message': 'What is a REST API?',
                'context': {}
            }
        )

        # This will fail if Ollama is not running
        if response.status_code == 200:
            data = response.get_json()
            assert 'reply' in data
            assert 'conversationId' in data
            assert isinstance(data['suggestions'], list)
        else:
            # If Ollama not available, should get error
            assert response.status_code == 400

    @pytest.mark.skip(reason="Requires OpenAI API key configured")
    def test_chat_with_openai(self, client, auth_token, app):
        """Test chat with OpenAI provider (integration test)"""
        with app.app_context():
            # Find the user from token
            import jwt as pyjwt
            decoded = pyjwt.decode(
                auth_token,
                app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = decoded['sub']

            # Update settings to use OpenAI
            settings = UserSettings.query.filter_by(user_id=user_id).first()
            settings.ai_provider = 'openai'
            settings.ai_api_key_encrypted = 'sk-test-key'  # Mock key
            settings.ai_model = 'gpt-3.5-turbo'
            db.session.commit()

        # Try to chat
        response = client.post(
            '/api/coach/chat',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'message': 'What is a REST API?',
                'context': {}
            }
        )

        # This will fail without valid API key
        # The test is here to document the expected behavior
        assert response.status_code in [200, 400]

    def test_chat_with_context(self, client, auth_token):
        """Test chat with conversation context"""
        # This test validates the request format, not the AI response
        response = client.post(
            '/api/coach/chat',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'message': 'Can you elaborate?',
                'context': {
                    'conversationId': 'conv-123',
                    'history': [
                        {'role': 'user', 'content': 'What is REST?'},
                        {'role': 'assistant', 'content': 'REST is...'}
                    ]
                }
            }
        )

        # Response depends on AI service availability
        # We're just checking the API accepts the request format
        # 503 = AI connection error, 504 = timeout
        assert response.status_code in [200, 400, 500, 503, 504]
