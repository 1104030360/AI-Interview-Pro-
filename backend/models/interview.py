from backend.database import db
from datetime import datetime
import uuid

class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, default='Untitled Interview')
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    actual_duration = db.Column(db.Integer, default=0)  # Duration in seconds

    # Video recording URLs
    video_url_cam0 = db.Column(db.String(500), nullable=True)  # Camera 0 video URL
    video_url_cam1 = db.Column(db.String(500), nullable=True)  # Camera 1 video URL

    # Relationships
    user = db.relationship('User', backref=db.backref('interviews', lazy='dynamic'))
    analysis = db.relationship('AnalysisReport', backref='interview', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'actualDuration': self.actual_duration,
            'videoUrlCam0': self.video_url_cam0,
            'videoUrlCam1': self.video_url_cam1,
            'analysis': self.analysis.to_dict() if self.analysis else None
        }
