"""
單元測試 - 認證服務

測試 AuthService 的核心功能：
- 使用者註冊
- 密碼驗證
- 使用者查詢
"""
import pytest
from backend.app import create_app
from backend.database import db
from backend.services.auth_service import AuthService
from backend.models.user import User

@pytest.fixture
def app():
    """建立測試用 Flask app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """建立測試 client"""
    return app.test_client()

def test_register_user(app):
    """測試使用者註冊功能"""
    with app.app_context():
        user = AuthService.register_user(
            email='unittest@example.com',
            password='testpass123',
            name='Unit Test User'
        )
        
        assert user is not None
        assert user.email == 'unittest@example.com'
        assert user.name == 'Unit Test User'
        assert user.role == 'user'
        # 密碼應該被雜湊，不是明文
        assert user.password_hash != 'testpass123'
        assert len(user.password_hash) > 50  # bcrypt hash 長度

def test_register_duplicate_email(app):
    """測試重複 email 註冊應該失敗"""
    with app.app_context():
        # 第一次註冊
        AuthService.register_user(
            email='duplicate@example.com',
            password='pass123',
            name='First User'
        )
        
        # 第二次註冊相同 email 應該拋出錯誤
        with pytest.raises(ValueError, match='Email already exists'):
            AuthService.register_user(
                email='duplicate@example.com',
                password='pass456',
                name='Second User'
            )

def test_authenticate_success(app):
    """測試正確密碼驗證成功"""
    with app.app_context():
        # 先註冊
        AuthService.register_user(
            email='auth@example.com',
            password='correctpass',
            name='Auth User'
        )

        # 驗證
        user = AuthService.authenticate('auth@example.com', 'correctpass')
        assert user is not None
        assert user.email == 'auth@example.com'

def test_authenticate_wrong_password(app):
    """測試錯誤密碼驗證失敗"""
    with app.app_context():
        # 先註冊
        AuthService.register_user(
            email='auth2@example.com',
            password='rightpass',
            name='Auth User 2'
        )
        
        # 錯誤密碼
        with pytest.raises(ValueError, match='Invalid password'):
            AuthService.authenticate('auth2@example.com', 'wrongpass')

def test_authenticate_nonexistent_user(app):
    """測試不存在的使用者驗證失敗"""
    with app.app_context():
        with pytest.raises(ValueError, match='User not found'):
            AuthService.authenticate('nonexistent@example.com', 'anypass')

def test_get_user_by_id(app):
    """測試根據 ID 查詢使用者"""
    with app.app_context():
        user = AuthService.register_user(
            email='lookup@example.com',
            password='pass123',
            name='Lookup User'
        )
        
        found_user = AuthService.get_user_by_id(user.id)
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == 'lookup@example.com'
        
def test_user_to_dict(app):
    """測試使用者序列化"""
    with app.app_context():
        user = AuthService.register_user(
            email='serialize@example.com',
            password='pass123',
            name='Serialize User'
        )
        
        user_dict = user.to_dict()
        assert 'id' in user_dict
        assert 'email' in user_dict
        assert 'name' in user_dict
        assert 'role' in user_dict
        assert 'created_at' in user_dict
        # 密碼不應該在序列化結果中
        assert 'password' not in user_dict
        assert 'password_hash' not in user_dict
