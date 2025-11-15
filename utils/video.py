"""
視訊處理工具模組

提供視訊錄製和格式轉換功能。
"""
import cv2
import ffmpeg
from pathlib import Path
from typing import Optional

from config import Config
from utils.logging_config import get_logger
from exceptions import EmotionAnalysisError

logger = get_logger(__name__)


def create_video_writer(
    output_path: str,
    fps: int,
    frame_size: tuple,
    fourcc_code: str = 'XVID'
) -> Optional[cv2.VideoWriter]:
    """
    建立視訊寫入器
    
    Args:
        output_path: 輸出檔案路徑
        fps: 影格率
        frame_size: 影格尺寸 (width, height)
        fourcc_code: 編碼格式 (如 'XVID', 'mp4v')
        
    Returns:
        VideoWriter 物件，失敗則返回 None
    """
    try:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_code)
        writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        
        if not writer.isOpened():
            logger.error(f"Failed to open video writer for {output_path}")
            return None
        
        logger.info(
            f"Video writer created: {output_path} "
            f"({frame_size[0]}x{frame_size[1]} @ {fps}fps)"
        )
        
        return writer
        
    except Exception as e:
        logger.error(f"Error creating video writer: {e}", exc_info=True)
        return None


def convert_avi_to_mp4(
    input_file: str,
    output_file: Optional[str] = None,
    remove_source: bool = False
) -> bool:
    """
    將 AVI 檔案轉換為 MP4 格式
    
    Args:
        input_file: 輸入 AVI 檔案路徑
        output_file: 輸出 MP4 檔案路徑（如未指定則自動生成）
        remove_source: 是否刪除原始檔案
        
    Returns:
        True 如果轉換成功，否則 False
    """
    try:
        # 如果未指定輸出檔案，自動生成
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.mp4'))
        
        # 檢查輸入檔案是否存在
        if not Path(input_file).exists():
            logger.error(f"Input file not found: {input_file}")
            return False
        
        logger.info(f"Converting {input_file} to {output_file}...")
        
        # 使用 ffmpeg 進行轉換
        (
            ffmpeg
            .input(input_file)
            .output(output_file)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        logger.info(f"Successfully converted to {output_file}")
        
        # 如果需要刪除原始檔案
        if remove_source:
            Path(input_file).unlink()
            logger.info(f"Removed source file: {input_file}")
        
        return True
        
    except ffmpeg.Error as e:
        logger.error(
            f"FFmpeg error during conversion: {e.stderr.decode()}",
            exc_info=True
        )
        return False
    except Exception as e:
        logger.error(f"Error converting video: {e}", exc_info=True)
        return False


def release_video_resources(*writers: cv2.VideoWriter) -> None:
    """
    釋放視訊寫入器資源
    
    Args:
        *writers: 一個或多個 VideoWriter 物件
    """
    for writer in writers:
        if writer is not None:
            try:
                writer.release()
                logger.debug("Video writer released")
            except Exception as e:
                logger.error(f"Error releasing video writer: {e}")


def get_video_info(video_path: str) -> Optional[dict]:
    """
    獲取視訊檔案資訊
    
    Args:
        video_path: 視訊檔案路徑
        
    Returns:
        包含視訊資訊的字典，失敗則返回 None
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        
        logger.info(f"Video info for {video_path}: {info}")
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting video info: {e}", exc_info=True)
        return None
