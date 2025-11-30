"""
Flask 後端 API Application

提供 RESTful API 服務，包含：
- JWT 使用者認證
- 面試記錄管理
- 分析報告查詢
- 使用者設定管理
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config_backend import Config
from backend.database import db, migrate, init_db
from backend.api.auth import auth_bp
from backend.api.analytics import analytics_bp
from backend.api.uploads import uploads_bp
from backend.api.analysis import analysis_bp
from backend.api.coach import coach_bp
from backend.api.questions import questions_bp
from backend.api.interviews import interviews_bp
from backend.api.settings import settings_bp

def create_app(config_class=Config):
    """Flask App Factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化擴充套件
    CORS(app, resources={
        r"/api/*": {
            "origins": config_class.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    JWTManager(app)
    init_db(app)

    # 驗證安全配置（生產環境必須設定 SECRET_KEY, JWT_SECRET_KEY, AI_SETTINGS_ENCRYPTION_KEY）
    config_class.validate_security_config()

    # 註冊 Blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(coach_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(interviews_bp)
    app.register_blueprint(settings_bp)

    # 開發工具 API (僅開發/測試環境)
    flask_env = os.getenv('FLASK_ENV', 'production')
    if flask_env in ['development', 'testing', 'local']:
        from backend.api.dev import dev_bp
        app.register_blueprint(dev_bp)
    
    # 全域錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
    
    # 健康檢查
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ai-interview-pro-backend',
            'version': '1.0.0'
        }), 200
    
    return app

# Create module-level app instance for imports
# (Allows background threads and other modules to import app)
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI Interview Pro Backend API Server")
    print("=" * 60)
    print(f"📍 Running on: http://0.0.0.0:5001")
    print(f"🔧 Debug mode: {app.config['DEBUG']}")
    print(f"💾 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
