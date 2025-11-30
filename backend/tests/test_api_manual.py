"""
API 手動測試腳本

測試所有 4 個認證 API endpoints:
1. POST /api/auth/register
2. POST /api/auth/login
3. POST /api/auth/refresh
4. GET /api/auth/me

注意：這些測試需要運行中的 Flask 伺服器 (localhost:5001)
請使用 `python backend/app.py` 啟動伺服器後，
直接執行 `python backend/tests/test_api_manual.py` 進行手動測試
"""
import pytest
import requests

# 跳過這些測試 - 需要運行中的伺服器
pytestmark = pytest.mark.skip(
    reason="Manual tests require running Flask server (localhost:5001). "
           "Run with: python backend/tests/test_api_manual.py"
)
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """測試健康檢查"""
    print("\n🔍 測試 1: Health Check")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check 通過!")
    
def test_register():
    """測試使用者註冊"""
    print("\n🔍 測試 2: Register User")
    print("=" * 50)
    
    data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ 註冊成功!")
        return response.json()
    elif 'already exists' in response.text:
        print("⚠️  使用者已存在，繼續測試登入...")
        return None
    else:
        print(f"❌ 註冊失敗: {response.text}")
        return None

def test_login():
    """測試使用者登入"""
    print("\n🔍 測試 3: Login User")
    print("=" * 50)
    
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ 登入成功!")
    return response.json()

def test_get_me(access_token):
    """測試取得使用者資訊"""
    print("\n🔍 測試 4: Get Current User")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ 取得使用者資訊成功!")
    
def test_refresh_token(refresh_token):
    """測試刷新 access token"""
    print("\n🔍 測試 5: Refresh Access Token")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = requests.post(f"{BASE_URL}/api/auth/refresh", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Token 刷新成功!")
    return response.json()

def run_all_tests():
    """執行所有測試"""
    print("\n" + "=" * 60)
    print("🚀 開始 API 測試")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Register (可能失敗如果使用者已存在)
        register_result = test_register()
        
        # Test 3: Login
        login_result = test_login()
        access_token = login_result['accessToken']
        refresh_token = login_result['refreshToken']
        
        # Test 4: Get current user
        test_get_me(access_token)
        
        # Test 5: Refresh token
        test_refresh_token(refresh_token)
        
        print("\n" + "=" * 60)
        print("✅ 所有測試通過!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 錯誤: 無法連接到伺服器")
        print("請確保 Flask 伺服器正在運行: python backend/app.py")
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
