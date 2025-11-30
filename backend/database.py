from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """初始化資料庫"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 匯入所有模型確保被註冊（必須在 init 之後）
    with app.app_context():
        import backend.models.user
        import backend.models.user_settings
        import backend.models.interview
        import backend.models.analysis_report
        import backend.models.question
