"""
攝影機管理工具模組

提供攝影機初始化、設定和錯誤處理功能。
"""
import cv2
import time
from typing import Optional

from config import Config
from utils.logging_config import get_logger
from exceptions import CameraOpenError, CameraReadError

logger = get_logger(__name__)


def open_camera_with_retry(
    camera_id: int,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> cv2.VideoCapture:
    """
    嘗試開啟攝影機，帶重試機制
    
    Args:
        camera_id: 攝影機 ID
        max_retries: 最大重試次數
        retry_delay: 重試延遲（秒）
        
    Returns:
        已開啟的 VideoCapture 物件
        
    Raises:
        CameraOpenError: 如果無法開啟攝影機
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Opening camera {camera_id} (attempt {attempt + 1})...")

            # 使用預設 backend（經測試比 AVFOUNDATION 快 7 倍）
            cap = cv2.VideoCapture(camera_id)
            logger.debug(f"Using default backend for camera {camera_id}")

            if not cap.isOpened():
                raise CameraOpenError(
                    f"Failed to open camera {camera_id}"
                )
            
            logger.info(f"Camera {camera_id} opened successfully")
            return cap
            
        except Exception as e:
            logger.error(
                f"Error opening camera {camera_id} "
                f"(attempt {attempt + 1}/{max_retries}): {e}"
            )
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise CameraOpenError(
                    f"Failed to open camera {camera_id} "
                    f"after {max_retries} attempts"
                )


def configure_camera(
    cap: cv2.VideoCapture,
    fps: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> bool:
    """
    設定攝影機參數
    
    Args:
        cap: VideoCapture 物件
        fps: 影格率
        width: 影像寬度
        height: 影像高度
        
    Returns:
        True 如果設定成功
    """
    try:
        config = Config()
        
        # 使用設定檔的預設值（如果未提供）
        if fps is None:
            fps = config.camera.TARGET_FPS
        if width is None:
            width = config.camera.CAMERA_WIDTH
        if height is None:
            height = config.camera.CAMERA_HEIGHT
        
        # 設定影格率
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        # 設定解析度
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # 驗證設定
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(
            f"Camera configured: {actual_width}x{actual_height} @ {actual_fps}fps"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error configuring camera: {e}", exc_info=True)
        return False


def read_frame(cap: cv2.VideoCapture) -> tuple:
    """
    從攝影機讀取一幀
    
    Args:
        cap: VideoCapture 物件
        
    Returns:
        Tuple[bool, Optional[np.ndarray]]: (成功與否, 影像幀)
        
    Raises:
        CameraReadError: 如果讀取失敗
    """
    try:
        ret, frame = cap.read()
        
        if not ret:
            raise CameraReadError("Failed to read frame from camera")
        
        return ret, frame
        
    except Exception as e:
        logger.error(f"Error reading frame: {e}", exc_info=True)
        raise CameraReadError(f"Failed to read frame: {e}")


def release_camera(*caps: cv2.VideoCapture) -> None:
    """
    釋放攝影機資源
    
    Args:
        *caps: 一個或多個 VideoCapture 物件
    """
    for cap in caps:
        if cap is not None:
            try:
                cap.release()
                logger.debug("Camera released")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")


def get_camera_info(cap: cv2.VideoCapture) -> dict:
    """
    獲取攝影機資訊
    
    Args:
        cap: VideoCapture 物件
        
    Returns:
        包含攝影機資訊的字典
    """
    try:
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'brightness': cap.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': cap.get(cv2.CAP_PROP_CONTRAST),
            'saturation': cap.get(cv2.CAP_PROP_SATURATION)
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting camera info: {e}", exc_info=True)
        return {}
