from backend.database import db
from backend.utils.crypto import decrypt_api_key


class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True)
    
    # Profile
    display_name = db.Column(db.String(100))
    job_role = db.Column(db.String(100))
    language = db.Column(db.String(10), default='en')
    avatar_url = db.Column(db.Text)  # Base64 或 URL
    
    # AI Config (加密儲存 API Key)
    ai_provider = db.Column(db.String(50), default='ollama')
    ai_api_key_encrypted = db.Column(db.Text)
    ai_model = db.Column(db.String(100), default='llama3:latest')
    
    # Prompts
    prompt_global = db.Column(db.Text)
    prompt_interview = db.Column(db.Text)
    prompt_coach = db.Column(db.Text)
    
    def to_dict(self):
        """序列化為字典 (前端格式)"""
        return {
            'profile': {
                'name': self.display_name or (self.user.name if hasattr(self, 'user') else ''),
                'role': self.job_role or '',
                'language': self.language,
                'avatarUrl': self.avatar_url
            },
            'ai': {
                'provider': self.ai_provider,
                'apiKey': decrypt_api_key(self.ai_api_key_encrypted) if self.ai_api_key_encrypted else '',
                'model': self.ai_model
            },
            'prompts': {
                'global': self.prompt_global or '',
                'interviewSuggestions': self.prompt_interview or '',
                'coachChat': self.prompt_coach or ''
            }
        }
