import os
from datetime import timedelta
from pathlib import Path

# 取得專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent

class Config:
    """後端 API 設定"""
    
    # Flask 基礎設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # 資料庫設定
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{PROJECT_ROOT}/interview_pro.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 設定
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # CORS 設定
    CORS_ORIGINS = [
        'http://localhost:3000',  # Vite dev server
        'http://localhost:3001',  # Vite dev server (備用端口)
        'http://localhost:5173',  # 另一個常見端口
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001',
        'http://127.0.0.1:5173',
    ]

    @staticmethod
    def validate_security_config():
        """
        驗證安全相關配置

        在應用啟動時調用，確保生產環境有正確的安全配置

        Raises:
            RuntimeError: 生產環境缺少必要的安全配置
        """
        env = os.getenv('FLASK_ENV', 'development')

        if env == 'production':
            # 檢查必要的安全配置
            if os.getenv('SECRET_KEY', '').startswith('dev-'):
                raise RuntimeError("SECRET_KEY must be set in production")

            if os.getenv('JWT_SECRET_KEY', '').startswith('jwt-secret'):
                raise RuntimeError("JWT_SECRET_KEY must be set in production")

            # 驗證加密金鑰
            from backend.utils.crypto import validate_encryption_key
            validate_encryption_key()
