"""
Background Analysis Task

Provides asynchronous video analysis execution using threading:
- Run analysis in background thread
- Track task status
- Handle errors gracefully
"""
import threading
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from backend.services.video_analysis_service import VideoAnalysisService
from backend.models.analysis_report import AnalysisReport
from backend.models.interview import Interview
from backend.database import db

logger = logging.getLogger(__name__)


class AnalysisTask:
    """
    Background task for video analysis

    Usage:
        task = AnalysisTask(interview_id, video_path)
        task.start()  # Run in background
    """

    # Track running tasks
    _active_tasks = {}
    _tasks_lock = threading.Lock()

    def __init__(self, interview_id: str, video_path: Path, camera: str = 'cam1'):
        """
        Initialize analysis task

        Args:
            interview_id: Interview UUID
            video_path: Path to uploaded video file
            camera: Camera identifier
        """
        self.interview_id = interview_id
        self.video_path = video_path
        self.camera = camera
        self.thread = None
        self.status = 'pending'
        self.progress = 0
        self.error = None
        self.started_at = None
        self.completed_at = None

    def start(self):
        """Start analysis task in background thread"""
        if self.thread and self.thread.is_alive():
            logger.warning(f"⚠️ Task for {self.interview_id} already running")
            return

        # Mark as pending in database first
        self._mark_pending()

        # Start background thread
        self.thread = threading.Thread(
            target=self._run_analysis,
            name=f"AnalysisTask-{self.interview_id[:8]}"
        )
        self.thread.daemon = True
        self.thread.start()

        # Track task
        with self._tasks_lock:
            self._active_tasks[self.interview_id] = self

        logger.info(f"🚀 Started analysis task for interview {self.interview_id}")

    def _run_analysis(self):
        """Internal: Run analysis (executed in background thread)"""
        from backend.app import app

        self.status = 'processing'
        self.started_at = datetime.utcnow()
        self.progress = 10

        logger.info(f"🎬 Running analysis for interview {self.interview_id}")

        # IMPORTANT: Run analysis within Flask app context
        with app.app_context():
            try:
                # Run video analysis
                report = VideoAnalysisService.analyze_interview(
                    self.interview_id,
                    self.video_path,
                    self.camera
                )

                if report:
                    self.status = 'completed'
                    self.progress = 100
                    logger.info(f"✅ Analysis completed for interview {self.interview_id}")
                else:
                    self.status = 'failed'
                    self.error = "Analysis returned no results"
                    logger.error(f"❌ Analysis failed for interview {self.interview_id}")

            except Exception as e:
                self.status = 'failed'
                self.error = str(e)
                logger.error(
                    f"❌ Analysis task failed for interview {self.interview_id}: {e}",
                    exc_info=True
                )

            finally:
                self.completed_at = datetime.utcnow()

                # Remove from active tasks
                with self._tasks_lock:
                    if self.interview_id in self._active_tasks:
                        del self._active_tasks[self.interview_id]

    def _mark_pending(self):
        """Mark analysis as pending in database"""
        try:
            # Create pending AnalysisReport
            from backend.app import app
            with app.app_context():
                report = AnalysisReport.query.filter_by(
                    interview_id=self.interview_id
                ).first()

                if not report:
                    report = AnalysisReport(
                        interview_id=self.interview_id,
                        status='pending'
                    )
                    db.session.add(report)
                else:
                    report.status = 'processing'

                db.session.commit()

        except Exception as e:
            logger.error(f"❌ Failed to mark analysis as pending: {e}")

    def get_status(self) -> dict:
        """
        Get current task status

        Returns:
            Status dictionary with progress, status, error
        """
        return {
            'status': self.status,
            'progress': self.progress,
            'error': self.error,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def get_task(cls, interview_id: str) -> Optional['AnalysisTask']:
        """
        Get active task by interview ID

        Args:
            interview_id: Interview UUID

        Returns:
            AnalysisTask or None if not found
        """
        with cls._tasks_lock:
            return cls._active_tasks.get(interview_id)

    @classmethod
    def get_all_active_tasks(cls) -> dict:
        """
        Get all active tasks

        Returns:
            Dictionary of interview_id -> task
        """
        with cls._tasks_lock:
            return cls._active_tasks.copy()


def start_analysis_task(interview_id: str, video_path: Path, camera: str = 'cam1'):
    """
    Convenience function to start analysis task

    Args:
        interview_id: Interview UUID
        video_path: Path to uploaded video file
        camera: Camera identifier

    Returns:
        AnalysisTask instance
    """
    task = AnalysisTask(interview_id, video_path, camera)
    task.start()
    return task
