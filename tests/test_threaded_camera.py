"""
ThreadedCamera 性能測試腳本

比較傳統 cv2.VideoCapture 和 ThreadedCamera 的性能差異。
"""

import sys
import time
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.threaded_camera import ThreadedCamera, AsyncCameraInitializer
from utils.logging_config import get_logger

logger = get_logger(__name__)


def test_traditional_camera(camera_id: int = 0, num_frames: int = 90):
    """
    測試 1: 傳統 cv2.VideoCapture 性能
    """
    print("\n" + "="*60)
    print("測試 1: 傳統 cv2.VideoCapture")
    print("="*60)

    # 開啟時間
    open_start = time.time()
    cap = cv2.VideoCapture(camera_id)
    open_time = time.time() - open_start

    if not cap.isOpened():
        print("✗ 無法開啟攝影機")
        return None

    print(f"開啟時間: {open_time*1000:.2f}ms")

    # 設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # 預熱
    for _ in range(5):
        cap.read()

    # 測試讀取性能
    print(f"測試讀取 {num_frames} 幀...")

    read_times = []
    loop_start = time.time()

    for i in range(num_frames):
        frame_start = time.time()
        ret, frame = cap.read()
        frame_time = time.time() - frame_start

        if ret:
            read_times.append(frame_time)
            # 模擬一些處理
            if i % 3 == 0:
                time.sleep(0.005)  # 5ms 模擬處理

    total_time = time.time() - loop_start

    cap.release()

    # 統計
    if read_times:
        avg_read = sum(read_times) / len(read_times)
        fps = num_frames / total_time

        print(f"\n結果:")
        print(f"  平均讀取時間: {avg_read*1000:.2f}ms")
        print(f"  總時間: {total_time:.2f}s")
        print(f"  實際 FPS: {fps:.1f}")

        return {
            'open_time': open_time,
            'avg_read_time': avg_read,
            'total_time': total_time,
            'fps': fps
        }

    return None


def test_threaded_camera(camera_id: int = 0, num_frames: int = 90):
    """
    測試 2: ThreadedCamera 性能
    """
    print("\n" + "="*60)
    print("測試 2: ThreadedCamera")
    print("="*60)

    # 開啟時間
    open_start = time.time()
    camera = ThreadedCamera(
        camera_id=camera_id,
        width=640,
        height=480,
        fps=30,
        buffer_size=2
    )
    success = camera.start()
    open_time = time.time() - open_start

    if not success:
        print("✗ 無法開啟攝影機")
        return None

    print(f"開啟時間: {open_time*1000:.2f}ms")

    # 等待穩定
    time.sleep(0.5)

    # 測試讀取性能
    print(f"測試讀取 {num_frames} 幀...")

    read_times = []
    loop_start = time.time()

    for i in range(num_frames):
        frame_start = time.time()
        ret, frame = camera.read()
        frame_time = time.time() - frame_start

        if ret:
            read_times.append(frame_time)
            # 模擬一些處理
            if i % 3 == 0:
                time.sleep(0.005)  # 5ms 模擬處理

    total_time = time.time() - loop_start

    # 獲取統計
    actual_fps = camera.get_fps()

    camera.stop()

    # 統計
    if read_times:
        avg_read = sum(read_times) / len(read_times)
        fps = num_frames / total_time

        print(f"\n結果:")
        print(f"  平均讀取時間: {avg_read*1000:.2f}ms")
        print(f"  總時間: {total_time:.2f}s")
        print(f"  循環 FPS: {fps:.1f}")
        print(f"  攝影機實際 FPS: {actual_fps:.1f}")

        return {
            'open_time': open_time,
            'avg_read_time': avg_read,
            'total_time': total_time,
            'fps': fps,
            'camera_fps': actual_fps
        }

    return None


def test_async_initialization():
    """
    測試 3: 異步初始化
    """
    print("\n" + "="*60)
    print("測試 3: 異步攝影機初始化")
    print("="*60)

    initializer = AsyncCameraInitializer()

    # 開始異步開啟
    async_start = time.time()
    initializer.start_opening(camera_id=0, width=640, height=480, fps=30)

    print("攝影機在背景開啟中...")
    print("主程式可以繼續做其他事情...")

    # 模擬其他初始化工作
    time.sleep(0.5)
    print("（模擬載入模型...）")
    time.sleep(0.5)
    print("（模擬其他初始化...）")

    # 等待攝影機準備好
    print("\n等待攝影機準備...")
    camera = initializer.wait_for_camera(timeout=5.0)
    total_time = time.time() - async_start

    if camera:
        print(f"✓ 攝影機準備完成")
        print(f"  總時間: {total_time:.2f}s")
        print(f"  優勢: 與其他初始化並行執行")

        # 測試讀取
        ret, frame = camera.read()
        if ret:
            print(f"✓ 成功讀取幀: {frame.shape}")

        camera.stop()
        return True
    else:
        print("✗ 攝影機初始化失敗")
        return False


def compare_performance():
    """
    比較性能
    """
    print("\n" + "="*60)
    print("性能比較")
    print("="*60)

    camera_id = 0
    num_frames = 90

    # 測試傳統方式
    traditional = test_traditional_camera(camera_id, num_frames)

    time.sleep(1)  # 讓攝影機完全釋放

    # 測試 ThreadedCamera
    threaded = test_threaded_camera(camera_id, num_frames)

    # 比較
    if traditional and threaded:
        print("\n" + "="*60)
        print("性能提升總結")
        print("="*60)

        open_speedup = traditional['open_time'] / threaded['open_time']
        read_speedup = traditional['avg_read_time'] / threaded['avg_read_time']
        fps_improvement = (threaded['fps'] - traditional['fps']) / traditional['fps'] * 100

        print(f"\n開啟速度:")
        print(f"  傳統: {traditional['open_time']*1000:.2f}ms")
        print(f"  Thread: {threaded['open_time']*1000:.2f}ms")
        print(f"  ✓ 提升: {open_speedup:.1f}x")

        print(f"\n讀取速度:")
        print(f"  傳統: {traditional['avg_read_time']*1000:.2f}ms")
        print(f"  Thread: {threaded['avg_read_time']*1000:.2f}ms")
        print(f"  ✓ 提升: {read_speedup:.1f}x")

        print(f"\n循環 FPS:")
        print(f"  傳統: {traditional['fps']:.1f}")
        print(f"  Thread: {threaded['fps']:.1f}")
        print(f"  ✓ 改善: +{fps_improvement:.1f}%")

        print(f"\n結論:")
        if read_speedup > 1.5:
            print(f"  🎉 ThreadedCamera 顯著更快 ({read_speedup:.1f}x)")
        elif read_speedup > 1.1:
            print(f"  ✓ ThreadedCamera 更快 ({read_speedup:.1f}x)")
        else:
            print(f"  ~ 性能相近")


def main():
    """
    執行所有測試
    """
    print("="*60)
    print("ThreadedCamera 性能測試")
    print("="*60)

    # 比較性能
    compare_performance()

    # 測試異步初始化
    test_async_initialization()

    print("\n" + "="*60)
    print("測試完成")
    print("="*60)


if __name__ == "__main__":
    main()
