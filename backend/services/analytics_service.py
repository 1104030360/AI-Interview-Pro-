"""
Analytics Service

Provides business logic for performance analytics and statistics:
- Performance trend calculation (time-series data)
- User summary statistics (aggregated metrics)
- Level calculation based on scores
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.database import db
from backend.models.interview import Interview
from backend.models.analysis_report import AnalysisReport


class AnalyticsService:
    """Service for analytics calculations and aggregations"""

    @staticmethod
    def calculate_trend(user_id: str, time_range: str, metric: str):
        """
        Calculate performance trend over time

        Args:
            user_id: User ID
            time_range: Time range ('1W', '1M', '3M', 'All')
            metric: Metric type ('Tone', 'Professionalism', 'Technical', 'Overall')

        Returns:
            dict: Performance trend data with date/value pairs
        """
        # Map time range to days
        days_map = {'1W': 7, '1M': 30, '3M': 90, 'All': 365}
        days = days_map.get(time_range, 7)
        start_date = datetime.utcnow() - timedelta(days=days)

        # Query completed interviews in the time range
        interviews = Interview.query.filter(
            Interview.user_id == user_id,
            Interview.created_at >= start_date,
            Interview.completed_at.isnot(None)
        ).order_by(Interview.created_at).all()

        # Aggregate data points
        data = []
        for interview in interviews:
            if interview.analysis and interview.analysis.status == 'completed':
                score = AnalyticsService._get_metric_score(interview.analysis, metric)
                data.append({
                    'date': interview.created_at.strftime('%b %d'),
                    'value': score
                })

        return {
            'timeRange': time_range,
            'metric': metric,
            'data': data
        }

    @staticmethod
    def _get_metric_score(analysis, metric):
        """
        Get score value for specific metric type

        Args:
            analysis: AnalysisReport instance
            metric: Metric type name

        Returns:
            float: Score value (0-100)
        """
        metric_map = {
            'Tone': analysis.empathy_score,
            'Professionalism': analysis.confidence_score,
            'Technical': analysis.technical_score,
            'Overall': analysis.overall_score
        }
        score = metric_map.get(metric, analysis.overall_score)
        return round(score, 1) if score else 0.0

    @staticmethod
    def get_user_summary(user_id: str):
        """
        Get user statistics summary

        Args:
            user_id: User ID

        Returns:
            dict: Summary statistics including sessions, scores, practice time, level
        """
        # Total completed sessions
        total_sessions = Interview.query.filter_by(
            user_id=user_id
        ).filter(Interview.completed_at.isnot(None)).count()

        # Average clarity score
        avg_clarity = db.session.query(
            func.avg(AnalysisReport.clarity_score)
        ).join(Interview).filter(
            Interview.user_id == user_id,
            AnalysisReport.status == 'completed'
        ).scalar() or 0.0

        # Total practice time (hours)
        total_duration = db.session.query(
            func.sum(Interview.actual_duration)
        ).filter_by(user_id=user_id).scalar() or 0
        practice_hours = round(total_duration / 3600, 1)

        # Calculate current level
        current_level = AnalyticsService._calculate_level(avg_clarity)

        return {
            'sessionsCompleted': total_sessions,
            'avgClarityScore': round(avg_clarity, 1),
            'practiceTimeHours': practice_hours,
            'currentLevel': current_level
        }

    @staticmethod
    def _calculate_level(score):
        """
        Calculate user level based on average score

        Args:
            score: Average score (0-100)

        Returns:
            str: Level grade ('S', 'A', 'B+', 'C')
        """
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        else:
            return 'C'
