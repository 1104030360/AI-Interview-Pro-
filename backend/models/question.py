from backend.database import db
from datetime import datetime
import uuid

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # Behavioral, Technical, System Design
    difficulty = db.Column(db.String(20))  # Junior, Mid, Senior
    role = db.Column(db.String(50))  # Frontend, Backend, PM, Data Science
    tags = db.Column(db.JSON)  # ['react', 'javascript', 'hooks']
    example_answer = db.Column(db.Text)
    created_by = db.Column(db.String(50), default='system')  # system or user_id
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'text': self.text,
            'type': self.type,
            'difficulty': self.difficulty,
            'role': self.role,
            'tags': self.tags or [],
            'exampleAnswer': self.example_answer,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
