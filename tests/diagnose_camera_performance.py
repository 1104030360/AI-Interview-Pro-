"""
攝影機性能診斷腳本

這個腳本測試攝影機各個環節的性能，找出延遲瓶頸。
"""

import sys
import time
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import get_logger
from config import Config

logger = get_logger(__name__)


def test_camera_open_time():
    """測試 1: 攝影機開啟時間"""
    print("\n" + "="*60)
    print("測試 1: 攝影機開啟時間")
    print("="*60)

    camera_id = 0

    # 測試 AVFOUNDATION backend
    print("\n使用 CAP_AVFOUNDATION:")
    start = time.time()
    cap1 = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
    open_time_avf = time.time() - start

    if cap1.isOpened():
        print(f"✓ 開啟成功: {open_time_avf*1000:.2f}ms")
        cap1.release()
    else:
        print(f"✗ 開啟失敗: {open_time_avf*1000:.2f}ms")

    time.sleep(0.5)

    # 測試預設 backend
    print("\n使用預設 backend:")
    start = time.time()
    cap2 = cv2.VideoCapture(camera_id)
    open_time_default = time.time() - start

    if cap2.isOpened():
        print(f"✓ 開啟成功: {open_time_default*1000:.2f}ms")
        cap2.release()
    else:
        print(f"✗ 開啟失敗: {open_time_default*1000:.2f}ms")

    print(f"\n建議: 使用 {'AVFOUNDATION' if open_time_avf < open_time_default else '預設'} backend")


def test_camera_read_performance():
    """測試 2: 攝影機讀取性能"""
    print("\n" + "="*60)
    print("測試 2: 攝影機讀取性能")
    print("="*60)

    camera_id = 0
    cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("✗ 無法開啟攝影機")
        return

    # 測試不同配置
    configs = [
        ("預設", None, None),
        ("低解析度 (320x240)", 320, 240),
        ("中解析度 (640x480)", 640, 480),
        ("高解析度 (1280x720)", 1280, 720),
    ]

    for config_name, width, height in configs:
        if width and height:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 預熱
        for _ in range(5):
            cap.read()

        # 測試讀取速度
        read_times = []
        for _ in range(30):
            start = time.time()
            ret, frame = cap.read()
            read_time = time.time() - start

            if ret:
                read_times.append(read_time)

        if read_times:
            avg_time = sum(read_times) / len(read_times)
            fps = 1.0 / avg_time if avg_time > 0 else 0

            print(f"\n{config_name}:")
            print(f"  實際解析度: {actual_width}x{actual_height}")
            print(f"  平均讀取時間: {avg_time*1000:.2f}ms")
            print(f"  實際 FPS: {fps:.1f}")

    cap.release()


def test_camera_configuration_time():
    """測試 3: 攝影機配置時間"""
    print("\n" + "="*60)
    print("測試 3: 攝影機配置時間")
    print("="*60)

    camera_id = 0
    cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("✗ 無法開啟攝影機")
        return

    # 測試配置時間
    start = time.time()
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    config_time = time.time() - start

    print(f"配置時間: {config_time*1000:.2f}ms")

    # 讀取實際配置
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"實際配置: {actual_width}x{actual_height} @ {actual_fps}fps")

    cap.release()


def test_dual_camera_performance():
    """測試 4: 雙攝影機同時讀取"""
    print("\n" + "="*60)
    print("測試 4: 雙攝影機同時讀取性能")
    print("="*60)

    # 嘗試開啟兩個攝影機
    cap0 = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    cap1 = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

    cameras = []
    if cap0.isOpened():
        cameras.append(("Camera 0", cap0))
        print("✓ Camera 0 已開啟")
    else:
        print("✗ Camera 0 無法開啟")

    if cap1.isOpened():
        cameras.append(("Camera 1", cap1))
        print("✓ Camera 1 已開啟")
    else:
        print("✗ Camera 1 無法開啟")

    if not cameras:
        print("✗ 沒有可用的攝影機")
        return

    # 測試同時讀取
    print(f"\n測試同時讀取 {len(cameras)} 個攝影機...")

    # 預熱
    for _ in range(5):
        for _, cap in cameras:
            cap.read()

    # 測試
    loop_times = []
    for _ in range(30):
        start = time.time()

        for _, cap in cameras:
            cap.read()

        loop_time = time.time() - start
        loop_times.append(loop_time)

    avg_loop_time = sum(loop_times) / len(loop_times)
    loop_fps = 1.0 / avg_loop_time if avg_loop_time > 0 else 0

    print(f"平均循環時間: {avg_loop_time*1000:.2f}ms")
    print(f"實際 FPS: {loop_fps:.1f}")
    print(f"每個攝影機平均: {avg_loop_time*1000/len(cameras):.2f}ms")

    # 釋放資源
    for _, cap in cameras:
        cap.release()


def test_current_config():
    """測試 5: 當前配置性能"""
    print("\n" + "="*60)
    print("測試 5: 當前配置性能")
    print("="*60)

    from config import Config
    config = Config()

    print(f"當前配置:")
    print(f"  TARGET_FPS: {config.camera.TARGET_FPS}")
    print(f"  CAMERA_WIDTH: {config.camera.CAMERA_WIDTH}")
    print(f"  CAMERA_HEIGHT: {config.camera.CAMERA_HEIGHT}")

    camera_id = 0
    cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("✗ 無法開啟攝影機")
        return

    # 應用當前配置
    cap.set(cv2.CAP_PROP_FPS, config.camera.TARGET_FPS)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.CAMERA_HEIGHT)

    # 預熱
    for _ in range(5):
        cap.read()

    # 測試
    read_times = []
    for _ in range(30):
        start = time.time()
        ret, frame = cap.read()
        read_time = time.time() - start

        if ret:
            read_times.append(read_time)

    if read_times:
        avg_time = sum(read_times) / len(read_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0

        print(f"\n性能測試結果:")
        print(f"  平均讀取時間: {avg_time*1000:.2f}ms")
        print(f"  實際 FPS: {fps:.1f}")

        if fps < 20:
            print(f"\n⚠️ 警告: 實際 FPS ({fps:.1f}) 偏低")
            print(f"   建議: 考慮提高 TARGET_FPS 或降低解析度")

    cap.release()


def print_recommendations():
    """打印優化建議"""
    print("\n" + "="*60)
    print("優化建議")
    print("="*60)

    recommendations = [
        "1. 提高 TARGET_FPS 到 30（目前是 5）",
        "2. 使用適當的解析度（320x240 適合快速處理）",
        "3. 考慮使用 AVFOUNDATION backend（macOS 上更快）",
        "4. 如果雙攝影機模式慢，考慮異步讀取",
        "5. 降低 Keras 分類頻率（不需要每幀都分類）",
    ]

    for rec in recommendations:
        print(f"  {rec}")


def main():
    """執行所有診斷測試"""
    print("="*60)
    print("攝影機性能診斷工具")
    print("="*60)

    tests = [
        test_camera_open_time,
        test_camera_read_performance,
        test_camera_configuration_time,
        test_dual_camera_performance,
        test_current_config,
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n✗ 測試失敗: {e}")
            import traceback
            traceback.print_exc()

    print_recommendations()

    print("\n" + "="*60)
    print("診斷完成")
    print("="*60)


if __name__ == "__main__":
    main()
