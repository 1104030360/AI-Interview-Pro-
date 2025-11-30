"""
Threaded Camera Module for Optimized Video Capture

基於以下資源的最佳實踐：
- Stack Overflow: Threading-based VideoCapture optimization
- Pysource 2024: Multi-threading approach for 2x performance
- OpenCV Forum: Buffer size optimization

核心優化：
1. 獨立執行緒持續讀取攝影機（非阻塞）
2. Buffer size 限制為 2（防止延遲堆積）
3. 異步初始化（不阻塞主程式）
4. 自動預熱機制
"""

import cv2
import time
import threading
from typing import Optional, Tuple
import numpy as np

from utils.logging_config import get_logger
from exceptions import CameraOpenError

logger = get_logger(__name__)


class ThreadedCamera:
    """
    執行緒化攝影機類別

    使用獨立執行緒持續讀取攝影機，提供非阻塞的幀獲取介面。
    相比傳統 cv2.VideoCapture，可以提升 2-3x 性能。

    Features:
    - 非阻塞幀讀取（always get latest frame）
    - Buffer size 優化（CAP_PROP_BUFFERSIZE=2）
    - 異步初始化（快速啟動）
    - 自動預熱機制

    Example:
        >>> camera = ThreadedCamera(camera_id=0)
        >>> camera.start()
        >>>
        >>> while True:
        >>>     ret, frame = camera.read()
        >>>     if ret:
        >>>         cv2.imshow('Frame', frame)
        >>>
        >>> camera.stop()
    """

    def __init__(
        self,
        camera_id: int = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        buffer_size: int = 2,
        warmup_frames: int = 5
    ):
        """
        初始化 ThreadedCamera

        Args:
            camera_id: 攝影機 ID
            width: 影像寬度
            height: 影像高度
            fps: 目標幀率
            buffer_size: OpenCV buffer 大小（建議 1-3）
            warmup_frames: 預熱幀數
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.buffer_size = buffer_size
        self.warmup_frames = warmup_frames

        # State
        self.capture = None
        self.frame = None
        self.status = False
        self.running = False

        # Threading
        self.thread = None
        self.lock = threading.Lock()

        # Performance tracking
        self.frame_count = 0
        self.start_time = None

        logger.info(
            f"ThreadedCamera initialized for camera {camera_id} "
            f"({width}x{height} @ {fps}fps, buffer={buffer_size})"
        )

    def _open_camera(self) -> bool:
        """
        開啟攝影機（內部方法）

        Returns:
            True if successful
        """
        try:
            logger.info(f"Opening camera {self.camera_id}...")

            # 使用預設 backend（診斷顯示比 AVFOUNDATION 快 7 倍）
            self.capture = cv2.VideoCapture(self.camera_id)

            if not self.capture.isOpened():
                raise CameraOpenError(f"Failed to open camera {self.camera_id}")

            # 關鍵優化：設定 buffer size 為 2（防止 frame 堆積）
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)

            # 設定解析度和 FPS
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)

            # 驗證設定
            actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.capture.get(cv2.CAP_PROP_FPS)

            logger.info(
                f"Camera {self.camera_id} opened: "
                f"{actual_width}x{actual_height} @ {actual_fps}fps"
            )

            # 預熱：讀取並丟棄前幾幀（加速穩定）
            logger.debug(f"Warming up camera {self.camera_id}...")
            for _ in range(self.warmup_frames):
                self.capture.read()

            logger.info(f"Camera {self.camera_id} ready")
            return True

        except Exception as e:
            logger.error(f"Error opening camera {self.camera_id}: {e}", exc_info=True)
            return False

    def start(self) -> bool:
        """
        啟動攝影機執行緒

        Returns:
            True if successful
        """
        if self.running:
            logger.warning(f"Camera {self.camera_id} already running")
            return True

        # 開啟攝影機
        if not self._open_camera():
            return False

        # 啟動讀取執行緒
        self.running = True
        self.start_time = time.time()

        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

        logger.info(f"Camera {self.camera_id} thread started")
        return True

    def _update_frame(self):
        """
        執行緒主循環：持續讀取最新幀

        這個方法在獨立執行緒中運行，持續從攝影機讀取幀。
        """
        logger.info(f"Camera {self.camera_id} update thread running")

        while self.running:
            if self.capture and self.capture.isOpened():
                try:
                    # 讀取幀
                    status, frame = self.capture.read()

                    # 使用 lock 保護共享資源
                    with self.lock:
                        self.status = status
                        if status:
                            self.frame = frame
                            self.frame_count += 1

                except Exception as e:
                    logger.error(f"Error reading frame from camera {self.camera_id}: {e}")
                    with self.lock:
                        self.status = False

            # 小延遲以避免 CPU 100%（根據目標 FPS）
            time.sleep(1.0 / (self.fps * 2))  # 稍微快於目標 FPS

        logger.info(f"Camera {self.camera_id} update thread stopped")

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        讀取最新幀（非阻塞）

        Returns:
            Tuple[bool, Optional[np.ndarray]]: (成功與否, 影像幀)
        """
        with self.lock:
            return self.status, self.frame.copy() if self.frame is not None else None

    def is_opened(self) -> bool:
        """
        檢查攝影機是否開啟

        Returns:
            True if camera is opened and running
        """
        return self.running and self.capture is not None and self.capture.isOpened()

    def get_fps(self) -> float:
        """
        獲取實際 FPS

        Returns:
            Frames per second
        """
        if self.start_time is None or self.frame_count == 0:
            return 0.0

        elapsed = time.time() - self.start_time
        return self.frame_count / elapsed if elapsed > 0 else 0.0

    def stop(self):
        """
        停止攝影機執行緒
        """
        logger.info(f"Stopping camera {self.camera_id}...")

        # 停止執行緒
        self.running = False

        # 等待執行緒結束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        # 釋放攝影機
        if self.capture:
            self.capture.release()
            self.capture = None

        # 記錄統計
        fps = self.get_fps()
        logger.info(
            f"Camera {self.camera_id} stopped: "
            f"total_frames={self.frame_count}, avg_fps={fps:.1f}"
        )

    def __enter__(self):
        """Context manager support"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.stop()


class AsyncCameraInitializer:
    """
    異步攝影機初始化器

    在背景執行緒開啟攝影機，不阻塞主程式。

    Example:
        >>> initializer = AsyncCameraInitializer()
        >>> initializer.start_opening(camera_id=0)
        >>>
        >>> # 在背景開啟時，可以做其他初始化...
        >>> # load_models()
        >>>
        >>> camera = initializer.wait_for_camera(timeout=5.0)
    """

    def __init__(self):
        """初始化異步攝影機初始化器"""
        self.camera = None
        self.thread = None
        self.error = None
        self.done = False
        self.lock = threading.Lock()

        logger.info("AsyncCameraInitializer created")

    def _init_camera(self, camera_id: int, **kwargs):
        """
        在背景執行緒開啟攝影機

        Args:
            camera_id: 攝影機 ID
            **kwargs: ThreadedCamera 參數
        """
        try:
            logger.info(f"Async initialization started for camera {camera_id}")

            camera = ThreadedCamera(camera_id=camera_id, **kwargs)
            success = camera.start()

            with self.lock:
                if success:
                    self.camera = camera
                    logger.info(f"Async initialization completed for camera {camera_id}")
                else:
                    self.error = f"Failed to start camera {camera_id}"
                    logger.error(self.error)

                self.done = True

        except Exception as e:
            with self.lock:
                self.error = str(e)
                self.done = True
                logger.error(f"Async initialization error: {e}", exc_info=True)

    def start_opening(self, camera_id: int, **kwargs):
        """
        開始在背景開啟攝影機

        Args:
            camera_id: 攝影機 ID
            **kwargs: ThreadedCamera 參數
        """
        self.thread = threading.Thread(
            target=self._init_camera,
            args=(camera_id,),
            kwargs=kwargs,
            daemon=True
        )
        self.thread.start()

        logger.info(f"Started async camera opening for camera {camera_id}")

    def is_ready(self) -> bool:
        """
        檢查攝影機是否準備好

        Returns:
            True if camera is ready
        """
        with self.lock:
            return self.done and self.camera is not None

    def wait_for_camera(self, timeout: float = 10.0) -> Optional[ThreadedCamera]:
        """
        等待攝影機開啟完成

        Args:
            timeout: 最大等待時間（秒）

        Returns:
            ThreadedCamera instance or None if timeout/error
        """
        start = time.time()

        while time.time() - start < timeout:
            with self.lock:
                if self.done:
                    if self.camera:
                        logger.info("Camera ready")
                        return self.camera
                    else:
                        logger.error(f"Camera initialization failed: {self.error}")
                        return None

            time.sleep(0.1)

        logger.error(f"Camera initialization timeout after {timeout}s")
        return None
