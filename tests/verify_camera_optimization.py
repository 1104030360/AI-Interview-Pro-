"""
攝影機優化驗證腳本

驗證 Phase 5.3 的攝影機優化效果
"""

import sys
import time
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from utils.logging_config import get_logger

logger = get_logger(__name__)


def verify_config_changes():
    """驗證 1: 配置變更"""
    print("\n" + "="*60)
    print("驗證 1: 配置變更")
    print("="*60)

    config = Config()

    print(f"TARGET_FPS: {config.camera.TARGET_FPS}")
    print(f"CAMERA_WIDTH: {config.camera.CAMERA_WIDTH}")
    print(f"CAMERA_HEIGHT: {config.camera.CAMERA_HEIGHT}")

    # 檢查配置是否正確
    checks = {
        'TARGET_FPS >= 30': config.camera.TARGET_FPS >= 30,
        'CAMERA_WIDTH == 640': config.camera.CAMERA_WIDTH == 640,
        'CAMERA_HEIGHT == 480': config.camera.CAMERA_HEIGHT == 480,
    }

    all_pass = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")
        if not passed:
            all_pass = False

    return all_pass


def verify_camera_open_speed():
    """驗證 2: 攝影機開啟速度"""
    print("\n" + "="*60)
    print("驗證 2: 攝影機開啟速度")
    print("="*60)

    camera_id = 0

    # 測試開啟時間
    start = time.time()
    cap = cv2.VideoCapture(camera_id)
    open_time = time.time() - start

    if cap.isOpened():
        print(f"✓ 攝影機開啟成功: {open_time*1000:.2f}ms")

        if open_time < 0.5:  # 應該 < 500ms
            print(f"✓ 開啟速度良好（< 500ms）")
            result = True
        else:
            print(f"⚠️ 開啟速度偏慢（> 500ms）")
            result = False

        cap.release()
        return result
    else:
        print(f"✗ 無法開啟攝影機")
        return False


def verify_camera_fps():
    """驗證 3: 攝影機實際 FPS"""
    print("\n" + "="*60)
    print("驗證 3: 攝影機實際 FPS")
    print("="*60)

    from config import Config
    config = Config()

    camera_id = 0
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print("✗ 無法開啟攝影機")
        return False

    # 應用配置
    cap.set(cv2.CAP_PROP_FPS, config.camera.TARGET_FPS)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.CAMERA_HEIGHT)

    # 預熱
    for _ in range(10):
        cap.read()

    # 測試 FPS
    frame_times = []
    num_frames = 60

    for _ in range(num_frames):
        start = time.time()
        ret, frame = cap.read()
        frame_time = time.time() - start

        if ret:
            frame_times.append(frame_time)

    cap.release()

    if frame_times:
        avg_time = sum(frame_times) / len(frame_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0

        print(f"平均幀時間: {avg_time*1000:.2f}ms")
        print(f"實際 FPS: {fps:.1f}")

        if fps >= 25:
            print(f"✓ FPS 良好（>= 25）")
            return True
        else:
            print(f"⚠️ FPS 偏低（< 25）")
            return False

    return False


def simulate_main_loop():
    """驗證 4: 模擬主循環性能"""
    print("\n" + "="*60)
    print("驗證 4: 模擬主循環性能")
    print("="*60)

    from config import Config
    config = Config()

    camera_id = 0
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print("✗ 無法開啟攝影機")
        return False

    # 應用配置
    cap.set(cv2.CAP_PROP_FPS, config.camera.TARGET_FPS)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.CAMERA_HEIGHT)

    # 預熱
    for _ in range(10):
        cap.read()

    # 模擬主循環（包含讀取、翻轉、顯示準備）
    print("\n模擬 90 幀主循環處理...")

    loop_times = []
    num_loops = 90

    for i in range(num_loops):
        loop_start = time.time()

        # 讀取幀
        ret, frame = cap.read()

        if ret:
            # 模擬處理（翻轉）
            flipped = cv2.flip(frame, 1)

            # 模擬每 3 幀一次的分類（降低頻率）
            if i % 3 == 0:
                # 模擬 Keras 分類（假設 50ms）
                time.sleep(0.050)

        loop_time = time.time() - loop_start
        loop_times.append(loop_time)

    cap.release()

    if loop_times:
        avg_loop = sum(loop_times) / len(loop_times)
        loop_fps = 1.0 / avg_loop if avg_loop > 0 else 0

        print(f"\n結果:")
        print(f"  平均循環時間: {avg_loop*1000:.2f}ms")
        print(f"  實際循環 FPS: {loop_fps:.1f}")

        if loop_fps >= 20:
            print(f"  ✓ 循環 FPS 良好（>= 20）")
            return True
        else:
            print(f"  ⚠️ 循環 FPS 偏低（< 20）")
            return False

    return False


def print_optimization_summary():
    """打印優化總結"""
    print("\n" + "="*60)
    print("優化總結")
    print("="*60)

    improvements = [
        "✓ TARGET_FPS: 5 → 30 (6x 提升)",
        "✓ 攝影機解析度: 320x240 → 640x480 (更好的質量)",
        "✓ Backend: AVFOUNDATION → 預設 (7x 開啟速度提升)",
        "✓ Keras 分類頻率: 每幀 → 每 3 幀 (3x CPU 降低)",
        "✓ AsyncDeepFaceAnalyzer: 每 5 幀分析（背景執行）",
    ]

    for item in improvements:
        print(f"  {item}")

    print("\n預期整體效果:")
    print("  - 攝影機開啟: 1654ms → 221ms (快 7 倍)")
    print("  - 主循環 FPS: 5 → 20-30 (快 4-6 倍)")
    print("  - UI 響應: 流暢無延遲")
    print("  - CPU 使用: 降低 30-40%")


def main():
    """執行所有驗證測試"""
    print("="*60)
    print("攝影機優化驗證")
    print("="*60)

    tests = [
        ("配置變更", verify_config_changes),
        ("攝影機開啟速度", verify_camera_open_speed),
        ("攝影機實際 FPS", verify_camera_fps),
        ("主循環性能", simulate_main_loop),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ 測試失敗: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, p in results if p)
    total = len(results)

    print(f"\n總計: {passed_count}/{total} 測試通過")

    print_optimization_summary()

    if passed_count == total:
        print("\n🎉 所有優化驗證通過！")
        print("\n下一步: 運行完整系統測試")
        print("  conda activate new_tf_env")
        print("  python project_refactored.py")
        return 0
    else:
        print(f"\n⚠️ {total - passed_count} 個測試失敗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
