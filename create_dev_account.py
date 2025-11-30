#!/usr/bin/env python3
"""
創建開發環境測試帳號
"""
import sys
sys.path.insert(0, '/Users/linjunting/Desktop/專題python')

from backend.app import create_app
from backend.services.auth_service import AuthService

def create_dev_account():
    """創建開發測試帳號"""
    app = create_app()
    
    with app.app_context():
        try:
            # 測試帳號資訊
            email = 'dev@test.com'
            password = 'dev123456'
            name = 'Developer Test'
            
            # 嘗試創建新帳號
            user = AuthService.register_user(
                email=email,
                password=password,
                name=name,
                role='user'
            )
            
            print(f'✅ 測試帳號創建成功！')
            print(f'📧 Email: {email}')
            print(f'🔐 Password: {password}')
            print(f'👤 Name: {name}')
            print(f'🆔 User ID: {user.id}')
            
        except ValueError as e:
            # 如果帳號已存在
            if 'already exists' in str(e).lower() or 'email' in str(e).lower():
                print(f'✅ 測試帳號已存在')
                print(f'📧 Email: {email}')
                print(f'🔐 Password: {password}')
            else:
                print(f'❌ 創建失敗: {e}')
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f'❌ 創建失敗: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_dev_account()
