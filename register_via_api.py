#!/usr/bin/env python3
"""
在運行中的後端創建測試帳號
直接通過HTTP API註冊
"""
import requests
import json

# 測試帳號資料
data = {
    "email": "dev@test.com",
    "password": "dev123456",
    "name": "Developer Test"
}

try:
    # 嘗試註冊
    response = requests.post(
        'http://localhost:5001/api/auth/register',
        headers={'Content-Type': 'application/json'},
        json=data
    )
    
    if response.status_code == 201:
        result = response.json()
        print('✅ 測試帳號創建成功！')
        print(f'📧 Email: {data["email"]}')
        print(f'🔐 Password: {data["password"]}')
        print(f'🆔 User ID: {result["userId"]}')
    elif response.status_code == 400:
        error = response.json()
        if 'already exists' in str(error).lower():
            print('✅ 測試帳號已存在')
            print(f'📧 Email: {data["email"]}')
            print(f'🔐 Password: {data["password"]}')
        else:
            print(f'❌ 錯誤: {error}')
    else:
        print(f'❌ 請求失敗: {response.status_code}')
        print(response.text)
        
except Exception as e:
    print(f'❌ 發生錯誤: {e}')
