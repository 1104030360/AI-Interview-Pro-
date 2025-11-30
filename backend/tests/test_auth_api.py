"""
Integration tests for Auth API endpoints
Tests registration, login, token refresh, and user info endpoints
"""
import pytest
import json
from backend.app import create_app
from backend.database import db


@pytest.fixture
def app():
    """Create test app with in-memory database"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAuthAPI:
    """Test suite for Auth API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'ai-interview-pro-backend'

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'name': 'New User'
        })

        assert response.status_code == 201
        data = json.loads(response.data)

        assert 'userId' in data
        assert data['email'] == 'newuser@example.com'
        assert data['name'] == 'New User'
        assert 'accessToken' in data
        assert 'refreshToken' in data

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/api/auth/register', json={
            'email': 'incomplete@example.com'
            # Missing password and name
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'MISSING_FIELDS'

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Register first user
        client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'password123',
            'name': 'First User'
        })

        # Try to register with same email
        response = client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'different_pass',
            'name': 'Second User'
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['code'] == 'REGISTRATION_FAILED'

    def test_login_success(self, client):
        """Test successful login"""
        # Register user first
        client.post('/api/auth/register', json={
            'email': 'login@example.com',
            'password': 'mypassword',
            'name': 'Login User'
        })

        # Login
        response = client.post('/api/auth/login', json={
            'email': 'login@example.com',
            'password': 'mypassword'
        })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['email'] == 'login@example.com'
        assert data['name'] == 'Login User'
        assert 'accessToken' in data
        assert 'refreshToken' in data

    def test_login_wrong_password(self, client):
        """Test login with wrong password"""
        # Register user
        client.post('/api/auth/register', json={
            'email': 'wrongpass@example.com',
            'password': 'correct_password',
            'name': 'User'
        })

        # Try to login with wrong password
        response = client.post('/api/auth/login', json={
            'email': 'wrongpass@example.com',
            'password': 'wrong_password'
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTHENTICATION_FAILED'

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'any_password'
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTHENTICATION_FAILED'

    def test_get_current_user(self, client):
        """Test getting current user info with valid token"""
        # Register and get token
        register_response = client.post('/api/auth/register', json={
            'email': 'getme@example.com',
            'password': 'password123',
            'name': 'Get Me User'
        })

        token = json.loads(register_response.data)['accessToken']

        # Get current user info
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['email'] == 'getme@example.com'
        assert data['name'] == 'Get Me User'

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get('/api/auth/me')

        assert response.status_code == 401  # Unauthorized

    def test_refresh_token(self, client):
        """Test refreshing access token"""
        # Register and get tokens
        register_response = client.post('/api/auth/register', json={
            'email': 'refresh@example.com',
            'password': 'password123',
            'name': 'Refresh User'
        })

        refresh_token = json.loads(register_response.data)['refreshToken']

        # Refresh access token
        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'accessToken' in data

    def test_refresh_with_access_token(self, client):
        """Test that refresh endpoint rejects access tokens"""
        # Register and get tokens
        register_response = client.post('/api/auth/register', json={
            'email': 'wrongtoken@example.com',
            'password': 'password123',
            'name': 'User'
        })

        access_token = json.loads(register_response.data)['accessToken']

        # Try to refresh with access token (should fail)
        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {access_token}'
        })

        assert response.status_code == 422  # Unprocessable Entity (wrong token type)

    def test_404_route(self, client):
        """Test 404 error handling"""
        response = client.get('/api/nonexistent')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error']['code'] == 'NOT_FOUND'
