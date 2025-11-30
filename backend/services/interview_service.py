"""
Interview Service

Business logic for managing interview records and sessions
"""
import uuid
from datetime import datetime
from backend.database import db
from backend.models.interview import Interview
from backend.models.analysis_report import AnalysisReport


class InterviewService:
    """Handle interview operations"""

    @staticmethod
    def get_user_interviews(user_id: str, page: int = 1, page_size: int = 20, keyword: str = '', mode: str = ''):
        """
        Get user's interview list with pagination and filtering

        Args:
            user_id: User UUID string
            page: Page number (default 1)
            page_size: Items per page (default 20)
            keyword: Search keyword for scenario/type
            mode: Filter by mode (Single/Dual)

        Returns:
            dict: {
                'items': [...],
                'pagination': {...}
            }
        """
        query = Interview.query.filter_by(user_id=user_id)

        # Keyword search
        if keyword:
            query = query.filter(
                (Interview.title.ilike(f'%{keyword}%')) |
                (Interview.status.ilike(f'%{keyword}%'))
            )

        # Mode filter (if needed in future when Interview model has mode field)
        # if mode:
        #     query = query.filter_by(mode=mode)

        # Sort and paginate
        query = query.order_by(Interview.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            'items': [interview.to_dict() for interview in pagination.items],
            'pagination': {
                'currentPage': page,
                'pageSize': page_size,
                'totalItems': pagination.total,
                'totalPages': pagination.pages
            }
        }

    @staticmethod
    def get_interview_detail(interview_id: str, user_id: str):
        """
        Get single interview details

        Args:
            interview_id: Interview UUID string
            user_id: User UUID string (for permission check)

        Returns:
            dict or None: Interview data or None if not found
        """
        interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
        return interview.to_dict() if interview else None

    @staticmethod
    def create_interview_session(user_id: str, title: str, status: str = 'pending'):
        """
        Create interview session

        Args:
            user_id: User UUID string
            title: Interview title/scenario
            status: Initial status (default 'pending')

        Returns:
            dict: {
                'sessionId': str,
                'uploadUrls': {...},
                'createdAt': str
            }
        """
        interview = Interview(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            status=status,
            created_at=datetime.utcnow()
        )

        db.session.add(interview)
        db.session.commit()

        # Generate upload URLs (placeholder)
        return {
            'sessionId': interview.id,
            'uploadUrls': {
                'camera0': f'/api/uploads/{interview.id}_cam0.webm',
                'camera1': f'/api/uploads/{interview.id}_cam1.webm'
            },
            'createdAt': interview.created_at.isoformat()
        }

    @staticmethod
    def complete_session(session_id: str, user_id: str, actual_duration: int, metadata: dict = None):
        """
        Complete session and trigger analysis

        Args:
            session_id: Interview UUID string
            user_id: User UUID string
            actual_duration: Duration in seconds
            metadata: Additional metadata (optional)

        Returns:
            dict: {
                'message': str,
                'interviewId': str,
                'analysisId': str,
                'estimatedCompletionTime': int
            }

        Raises:
            ValueError: If session not found
        """
        interview = Interview.query.filter_by(id=session_id, user_id=user_id).first()

        if not interview:
            raise ValueError('Session not found')

        # Update interview info
        interview.actual_duration = actual_duration
        interview.completed_at = datetime.utcnow()
        interview.status = 'completed'
        db.session.commit()

        # Create analysis report (placeholder - actual analysis triggered separately)
        analysis = AnalysisReport(
            interview_id=session_id,
            status='queued',
            progress=0,
            created_at=datetime.utcnow()
        )
        db.session.add(analysis)
        db.session.commit()

        # TODO: Trigger actual analysis system (EmotionAnalysisSystem integration)
        # This could be done via:
        # 1. Subprocess call to project_refactored.py
        # 2. Background task queue (Celery)
        # 3. Direct function call if refactored as module

        return {
            'message': 'Analysis queued',
            'interviewId': session_id,
            'analysisId': analysis.id,
            'estimatedCompletionTime': 60  # Estimated 60 seconds
        }

    @staticmethod
    def delete_interview(interview_id: str, user_id: str):
        """
        Delete interview record

        Args:
            interview_id: Interview UUID string
            user_id: User UUID string (for permission check)

        Returns:
            bool: True if deleted, False if not found

        Raises:
            ValueError: If interview not found
        """
        interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()

        if not interview:
            raise ValueError('Interview not found')

        db.session.delete(interview)
        db.session.commit()

        return True
