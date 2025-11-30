# 匯出所有 API blueprints
from backend.api.auth import auth_bp
from backend.api.analytics import analytics_bp
from backend.api.uploads import uploads_bp
from backend.api.analysis import analysis_bp
from backend.api.interviews import interviews_bp
from backend.api.settings import settings_bp
from backend.api.coach import coach_bp
from backend.api.questions import questions_bp

__all__ = [
    'auth_bp',
    'analytics_bp',
    'uploads_bp',
    'analysis_bp',
    'interviews_bp',
    'settings_bp',
    'coach_bp',
    'questions_bp'
]
