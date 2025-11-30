"""
Integration tests for Analytics API

Tests:
- GET /api/analytics/performance-trend
- GET /api/analytics/summary
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.interview import Interview
from backend.models.analysis_report import AnalysisReport
from backend.services.auth_service import AuthService
from datetime import datetime, timedelta
import uuid


@pytest.fixture
def app():
    """Create application for testing"""
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


@pytest.fixture
def auth_headers(client, app):
    """Create authenticated user and return auth headers"""
    with app.app_context():
        # Create test user
        user = AuthService.register_user(
            email="analytics@test.com",
            password="testpass123",
            name="Analytics Test"
        )

        # Create test interviews with analysis
        base_date = datetime.utcnow() - timedelta(days=14)

        for i in range(5):
            interview = Interview(
                id=str(uuid.uuid4()),
                user_id=user.id,
                title=f"Test Interview {i+1}",
                status='completed',
                created_at=base_date + timedelta(days=i*3),
                completed_at=base_date + timedelta(days=i*3, hours=1),
                actual_duration=3600
            )
            db.session.add(interview)

            report = AnalysisReport(
                id=str(uuid.uuid4()),
                interview_id=interview.id,
                status='completed',
                overall_score=70 + (i * 5),
                empathy_score=65 + (i * 5),
                confidence_score=70 + (i * 5),
                technical_score=72 + (i * 5),
                clarity_score=68 + (i * 5)
            )
            db.session.add(report)

        db.session.commit()

    # Login to get token
    response = client.post('/api/auth/login', json={
        'email': 'analytics@test.com',
        'password': 'testpass123'
    })
    data = response.get_json()
    token = data['accessToken']

    return {'Authorization': f'Bearer {token}'}


class TestAnalyticsAPI:
    """Test Analytics API endpoints"""

    def test_get_performance_trend_default_params(self, client, auth_headers):
        """Test GET /api/analytics/performance-trend with default params"""
        response = client.get(
            '/api/analytics/performance-trend',
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert 'timeRange' in data
        assert 'metric' in data
        assert 'data' in data
        assert data['timeRange'] == '1W'
        assert data['metric'] == 'Professionalism'
        assert isinstance(data['data'], list)

    def test_get_performance_trend_custom_params(self, client, auth_headers):
        """Test GET /api/analytics/performance-trend with custom params"""
        response = client.get(
            '/api/analytics/performance-trend?timeRange=1M&metric=Technical',
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data['timeRange'] == '1M'
        assert data['metric'] == 'Technical'
        assert len(data['data']) > 0  # Should have data points

        # Validate data structure
        for point in data['data']:
            assert 'date' in point
            assert 'value' in point
            assert isinstance(point['value'], (int, float))

    def test_get_performance_trend_invalid_range(self, client, auth_headers):
        """Test GET /api/analytics/performance-trend with invalid time range"""
        response = client.get(
            '/api/analytics/performance-trend?timeRange=INVALID',
            headers=auth_headers
        )
        assert response.status_code == 400

        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_TIME_RANGE'

    def test_get_performance_trend_invalid_metric(self, client, auth_headers):
        """Test GET /api/analytics/performance-trend with invalid metric"""
        response = client.get(
            '/api/analytics/performance-trend?metric=INVALID',
            headers=auth_headers
        )
        assert response.status_code == 400

        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_METRIC'

    def test_get_performance_trend_unauthorized(self, client):
        """Test GET /api/analytics/performance-trend without auth"""
        response = client.get('/api/analytics/performance-trend')
        assert response.status_code == 401

    def test_get_summary(self, client, auth_headers):
        """Test GET /api/analytics/summary"""
        response = client.get(
            '/api/analytics/summary',
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert 'sessionsCompleted' in data
        assert 'avgClarityScore' in data
        assert 'practiceTimeHours' in data
        assert 'currentLevel' in data

        # Validate data types and values
        assert isinstance(data['sessionsCompleted'], int)
        assert data['sessionsCompleted'] == 5  # We created 5 interviews

        assert isinstance(data['avgClarityScore'], (int, float))
        assert 0 <= data['avgClarityScore'] <= 100

        assert isinstance(data['practiceTimeHours'], (int, float))
        assert data['practiceTimeHours'] > 0  # 5 hours total

        assert isinstance(data['currentLevel'], str)
        assert data['currentLevel'] in ['S', 'A', 'B+', 'C']

    def test_get_summary_unauthorized(self, client):
        """Test GET /api/analytics/summary without auth"""
        response = client.get('/api/analytics/summary')
        assert response.status_code == 401

    def test_get_summary_empty_data(self, client, app):
        """Test GET /api/analytics/summary with no interview data"""
        with app.app_context():
            # Create new user with no interviews
            user = AuthService.register_user(
                email="empty@test.com",
                password="testpass123",
                name="Empty User"
            )
            db.session.commit()

        # Login as empty user
        response = client.post('/api/auth/login', json={
            'email': 'empty@test.com',
            'password': 'testpass123'
        })
        data = response.get_json()
        token = data['accessToken']
        headers = {'Authorization': f'Bearer {token}'}

        # Get summary
        response = client.get('/api/analytics/summary', headers=headers)
        assert response.status_code == 200

        data = response.get_json()
        assert data['sessionsCompleted'] == 0
        assert data['avgClarityScore'] == 0.0
        assert data['practiceTimeHours'] == 0.0
        assert data['currentLevel'] == 'C'  # Default for score 0
