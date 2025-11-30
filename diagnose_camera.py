#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
攝影機診斷工具
用於診斷 macOS 上的 OpenCV 攝影機問題
"""

import cv2
import sys

def print_opencv_info():
    """顯示 OpenCV 版本和構建信息"""
    print("=" * 60)
    print("OpenCV 診斷信息")
    print("=" * 60)
    print(f"OpenCV 版本: {cv2.__version__}")
    print(f"構建信息:")
    print(cv2.getBuildInformation())
    print("=" * 60)
    print()

def test_camera_detailed(camera_id, backend=None):
    """詳細測試指定的攝影機"""
    print(f"\n{'='*60}")
    print(f"測試攝影機 {camera_id}" + (f" (後端: {backend})" if backend else ""))
    print("=" * 60)
    
    try:
        # 根據後端創建 VideoCapture
        if backend == "AVFOUNDATION":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
        elif backend == "ANY":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_ANY)
        else:
            cap = cv2.VideoCapture(camera_id)
        
        # 檢查是否成功開啟
        if not cap.isOpened():
            print(f"❌ 無法開啟攝影機 {camera_id}")
            return False
        
        print(f"✅ 攝影機 {camera_id} 開啟成功")
        
        # 獲取攝影機屬性
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        backend_name = cap.getBackendName()
        
        print(f"   解析度: {width}x{height}")
        print(f"   FPS: {fps}")
        print(f"   後端: {backend_name}")
        
        # 嘗試讀取 5 幀
        print(f"\n   嘗試讀取 5 幀...")
        success_count = 0
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                success_count += 1
                print(f"   ✅ 第 {i+1} 幀: 成功 (解析度: {frame.shape[1]}x{frame.shape[0]})")
            else:
                print(f"   ❌ 第 {i+1} 幀: 失敗")
        
        cap.release()
        
        if success_count == 5:
            print(f"\n✅ 攝影機 {camera_id} 完全可用！")
            return True
        elif success_count > 0:
            print(f"\n⚠️  攝影機 {camera_id} 部分可用 ({success_count}/5 幀)")
            return False
        else:
            print(f"\n❌ 攝影機 {camera_id} 無法讀取畫面")
            return False
            
    except Exception as e:
        print(f"❌ 測試攝影機 {camera_id} 時發生錯誤: {e}")
        return False

def main():
    """主函式"""
    print("\n" + "=" * 60)
    print("macOS OpenCV 攝影機診斷工具")
    print("=" * 60)
    
    # 顯示 OpenCV 信息
    print_opencv_info()
    
    # 測試攝影機 0 到 2，使用不同的後端
    print("\n" + "=" * 60)
    print("開始測試攝影機...")
    print("=" * 60)
    
    working_cameras = []
    
    # 測試不同的攝影機 ID 和後端組合
    for camera_id in range(3):
        # 測試預設後端
        if test_camera_detailed(camera_id):
            working_cameras.append((camera_id, "default"))
        
        # 測試 AVFOUNDATION 後端（macOS 專用）
        if test_camera_detailed(camera_id, "AVFOUNDATION"):
            working_cameras.append((camera_id, "AVFOUNDATION"))
    
    # 總結
    print("\n" + "=" * 60)
    print("診斷結果總結")
    print("=" * 60)
    
    if working_cameras:
        print("✅ 找到以下可用的攝影機：")
        for cam_id, backend in working_cameras:
            print(f"   - 攝影機 {cam_id} (後端: {backend})")
        
        print("\n📝 建議：")
        cam_id, backend = working_cameras[0]
        print(f"   請在 .env 檔案中設定 CAMERA_0_ID={cam_id}")
        if backend == "AVFOUNDATION":
            print(f"   並在程式中使用: cv2.VideoCapture({cam_id}, cv2.CAP_AVFOUNDATION)")
    else:
        print("❌ 未找到任何可用的攝影機")
        print("\n可能的原因：")
        print("   1. Terminal 沒有攝影機存取權限")
        print("      → 檢查：系統設定 > 隱私權與安全性 > 相機")
        print("   2. 攝影機被其他應用程式佔用")
        print("      → 關閉所有使用攝影機的應用程式（Zoom、FaceTime 等）")
        print("   3. 使用 Continuity Camera 但 OpenCV 版本不支援")
        print("      → 嘗試使用 Mac 內建攝影機或更新 OpenCV")
        print("   4. OpenCV 版本過舊")
        print("      → 執行: pip install --upgrade opencv-python")

if __name__ == "__main__":
    main()
