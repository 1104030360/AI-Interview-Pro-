#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
簡單的攝影機測試腳本
用於驗證攝影機權限和可用性
"""

import cv2
import sys

def test_camera(camera_id=0):
    """測試指定的攝影機"""
    print(f"正在測試攝影機 {camera_id}...")
    
    cap = cv2.VideoCapture(camera_id)
    
    if cap.isOpened():
        print(f"✅ 攝影機 {camera_id} 開啟成功！")
        
        # 嘗試讀取一幀
        ret, frame = cap.read()
        if ret:
            print(f"✅ 成功讀取畫面，解析度: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print(f"❌ 無法讀取畫面")
        
        cap.release()
        return True
    else:
        print(f"❌ 攝影機 {camera_id} 開啟失敗")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("攝影機權限測試")
    print("=" * 50)
    
    # 測試攝影機 0
    cam0_ok = test_camera(0)
    
    print()
    
    # 測試攝影機 1
    cam1_ok = test_camera(1)
    
    print()
    print("=" * 50)
    print("測試結果摘要：")
    print(f"  攝影機 0: {'✅ 可用' if cam0_ok else '❌ 不可用'}")
    print(f"  攝影機 1: {'✅ 可用' if cam1_ok else '❌ 不可用'}")
    print("=" * 50)
    
    if not cam0_ok:
        print("\n⚠️  攝影機 0 無法使用，可能的原因：")
        print("  1. Terminal 沒有攝影機權限")
        print("  2. 攝影機被其他應用程式佔用")
        print("  3. 攝影機硬體故障")
        print("\n請檢查：系統偏好設定 > 隱私權與安全性 > 相機")
