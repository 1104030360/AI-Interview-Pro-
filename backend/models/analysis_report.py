from backend.database import db
from datetime import datetime
import uuid

class AnalysisReport(db.Model):
    __tablename__ = 'analysis_reports'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = db.Column(db.String(36), db.ForeignKey('interviews.id'), nullable=False, unique=True, index=True)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed

    # Score fields (0-100)
    overall_score = db.Column(db.Float, default=0.0)
    empathy_score = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    technical_score = db.Column(db.Float, default=0.0)
    clarity_score = db.Column(db.Float, default=0.0)

    # Additional analysis data (JSON)
    emotion_data = db.Column(db.JSON, nullable=True)  # Detailed emotion timeline
    suggestions = db.Column(db.JSON, nullable=True)   # AI-generated suggestions

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'interviewId': self.interview_id,
            'status': self.status,
            'overallScore': round(self.overall_score, 1) if self.overall_score else 0.0,
            'empathyScore': round(self.empathy_score, 1) if self.empathy_score else 0.0,
            'confidenceScore': round(self.confidence_score, 1) if self.confidence_score else 0.0,
            'technicalScore': round(self.technical_score, 1) if self.technical_score else 0.0,
            'clarityScore': round(self.clarity_score, 1) if self.clarity_score else 0.0,
            'emotionData': self.emotion_data,
            'suggestions': self.suggestions,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
