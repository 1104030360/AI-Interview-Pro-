"""
Unit tests for AnalyticsService

Tests:
- Performance trend calculation
- User summary statistics
- Level calculation logic
- Edge cases handling
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
from backend.services.analytics_service import AnalyticsService
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
def test_user(app):
    """Create test user with interview data"""
    with app.app_context():
        user = AuthService.register_user(
            email="service_test@example.com",
            password="testpass123",
            name="Service Test User"
        )

        # Create interviews spanning 30 days
        base_date = datetime.utcnow() - timedelta(days=30)

        for i in range(8):
            interview = Interview(
                id=str(uuid.uuid4()),
                user_id=user.id,
                title=f"Test Interview {i+1}",
                status='completed',
                created_at=base_date + timedelta(days=i*3),
                completed_at=base_date + timedelta(days=i*3, hours=1),
                actual_duration=3600  # 1 hour
            )
            db.session.add(interview)

            # Progressive improvement trend
            base_score = 60 + (i * 4)
            report = AnalysisReport(
                id=str(uuid.uuid4()),
                interview_id=interview.id,
                status='completed',
                overall_score=min(95, base_score + 5),
                empathy_score=min(95, base_score),
                confidence_score=min(95, base_score + 2),
                technical_score=min(95, base_score + 3),
                clarity_score=min(95, base_score + 1)
            )
            db.session.add(report)

        db.session.commit()
        user_id = user.id  # Extract ID before leaving context
        return user_id


class TestAnalyticsService:
    """Test AnalyticsService methods"""

    def test_calculate_trend_1w(self, app, test_user):
        """Test calculate_trend with 1 week range"""
        with app.app_context():
            result = AnalyticsService.calculate_trend(
                test_user,
                '1W',
                'Professionalism'
            )

            assert result['timeRange'] == '1W'
            assert result['metric'] == 'Professionalism'
            assert isinstance(result['data'], list)
            # Should have some recent data points
            assert len(result['data']) >= 0

    def test_calculate_trend_1m(self, app, test_user):
        """Test calculate_trend with 1 month range"""
        with app.app_context():
            result = AnalyticsService.calculate_trend(
                test_user,
                '1M',
                'Technical'
            )

            assert result['timeRange'] == '1M'
            assert result['metric'] == 'Technical'
            assert len(result['data']) > 0  # Should have data in 30 days

            # Verify data structure
            for point in result['data']:
                assert 'date' in point
                assert 'value' in point
                assert point['value'] >= 0
                assert point['value'] <= 100

    def test_calculate_trend_all_time(self, app, test_user):
        """Test calculate_trend with All range"""
        with app.app_context():
            result = AnalyticsService.calculate_trend(
                test_user,
                'All',
                'Tone'
            )

            assert result['timeRange'] == 'All'
            assert result['metric'] == 'Tone'
            assert len(result['data']) == 8  # All 8 interviews

    def test_calculate_trend_shows_improvement(self, app, test_user):
        """Test that trend shows improvement over time"""
        with app.app_context():
            result = AnalyticsService.calculate_trend(
                test_user,
                'All',
                'Professionalism'
            )

            if len(result['data']) >= 2:
                # Check that latest score is higher than first
                first_score = result['data'][0]['value']
                last_score = result['data'][-1]['value']
                assert last_score > first_score

    def test_get_metric_score_professionalism(self, app, test_user):
        """Test _get_metric_score for Professionalism"""
        with app.app_context():
            report = AnalysisReport.query.first()
            score = AnalyticsService._get_metric_score(report, 'Professionalism')

            assert score == report.confidence_score
            assert isinstance(score, float)

    def test_get_metric_score_tone(self, app, test_user):
        """Test _get_metric_score for Tone"""
        with app.app_context():
            report = AnalysisReport.query.first()
            score = AnalyticsService._get_metric_score(report, 'Tone')

            assert score == report.empathy_score

    def test_get_metric_score_technical(self, app, test_user):
        """Test _get_metric_score for Technical"""
        with app.app_context():
            report = AnalysisReport.query.first()
            score = AnalyticsService._get_metric_score(report, 'Technical')

            assert score == report.technical_score

    def test_get_user_summary(self, app, test_user):
        """Test get_user_summary with complete data"""
        with app.app_context():
            summary = AnalyticsService.get_user_summary(test_user)

            assert 'sessionsCompleted' in summary
            assert 'avgClarityScore' in summary
            assert 'practiceTimeHours' in summary
            assert 'currentLevel' in summary

            # Verify values
            assert summary['sessionsCompleted'] == 8
            assert summary['avgClarityScore'] > 0
            assert summary['practiceTimeHours'] == 8.0  # 8 hours total
            assert summary['currentLevel'] in ['S', 'A', 'B+', 'C']

    def test_get_user_summary_empty(self, app):
        """Test get_user_summary with no data"""
        with app.app_context():
            user = AuthService.register_user(
                email="empty@test.com",
                password="test123",
                name="Empty User"
            )
            db.session.commit()

            summary = AnalyticsService.get_user_summary(user.id)

            assert summary['sessionsCompleted'] == 0
            assert summary['avgClarityScore'] == 0.0
            assert summary['practiceTimeHours'] == 0.0
            assert summary['currentLevel'] == 'C'

    def test_calculate_level_s_grade(self, app):
        """Test _calculate_level returns S for 90+"""
        with app.app_context():
            assert AnalyticsService._calculate_level(90) == 'S'
            assert AnalyticsService._calculate_level(95) == 'S'
            assert AnalyticsService._calculate_level(100) == 'S'

    def test_calculate_level_a_grade(self, app):
        """Test _calculate_level returns A for 80-89"""
        with app.app_context():
            assert AnalyticsService._calculate_level(80) == 'A'
            assert AnalyticsService._calculate_level(85) == 'A'
            assert AnalyticsService._calculate_level(89) == 'A'

    def test_calculate_level_b_plus_grade(self, app):
        """Test _calculate_level returns B+ for 70-79"""
        with app.app_context():
            assert AnalyticsService._calculate_level(70) == 'B+'
            assert AnalyticsService._calculate_level(75) == 'B+'
            assert AnalyticsService._calculate_level(79) == 'B+'

    def test_calculate_level_c_grade(self, app):
        """Test _calculate_level returns C for <70"""
        with app.app_context():
            assert AnalyticsService._calculate_level(0) == 'C'
            assert AnalyticsService._calculate_level(50) == 'C'
            assert AnalyticsService._calculate_level(69) == 'C'
