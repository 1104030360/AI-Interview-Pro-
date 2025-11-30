import bcrypt
import uuid
from backend.models.user import User
from backend.models.user_settings import UserSettings
from backend.database import db

class AuthService:
    @staticmethod
    def register_user(email: str, password: str, name: str, role: str = 'user'):
        """註冊新使用者"""
        # 驗證電子郵件唯一性
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already exists')
        
        # 密碼雜湊
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # 建立使用者
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=password_hash,
            name=name,
            role=role
        )
        
        db.session.add(user)
        
        # 建立預設設定
        default_settings = UserSettings(
            user_id=user.id,
            display_name=name,
            ai_provider='ollama',
            ai_model='llama3:latest'
        )
        db.session.add(default_settings)
        
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate(email: str, password: str):
        """驗證使用者"""
        print(f'🔍 嘗試登入: {email}')
        user = User.query.filter_by(email=email).first()
        print(f'🔍 查詢結果: {user}')
        
        if not user:
            print(f'❌ 找不到使用者: {email}')
            raise ValueError('User not found')
        
        print(f'🔍 驗證密碼...')
        if not bcrypt.checkpw(
            password.encode('utf-8'), 
            user.password_hash.encode('utf-8')
        ):
            print(f'❌ 密碼錯誤')
            raise ValueError('Invalid password')
        
        print(f'✅ 認證成功: {email}')
        return user
    
    @staticmethod
    def get_user_by_id(user_id: str):
        """根據 ID 取得使用者"""
        return db.session.get(User, user_id)
