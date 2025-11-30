"""
影像分類工具模組

提供影像預處理和分類功能，封裝 Keras 模型的預測邏輯。
"""
import cv2
import numpy as np
from typing import Tuple
from keras.models import Model

from config import Config
from utils.logging_config import get_logger

logger = get_logger(__name__)


def preprocess_frame(frame: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    預處理影像幀以供 Keras 模型使用
    
    Args:
        frame: 原始影像幀
        target_size: 目標尺寸 (width, height)
        
    Returns:
        預處理後的影像陣列，形狀為 (1, height, width, 3)
    """
    try:
        # 調整大小
        resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
        
        # 轉換為浮點數
        image_array = np.asarray(resized, dtype=np.float32)
        
        # 正規化到 [-1, 1]
        normalized = (image_array / 127.5) - 1
        
        # 增加批次維度
        batched = normalized.reshape(1, target_size[1], target_size[0], 3)
        
        return batched
        
    except Exception as e:
        logger.error(f"Error preprocessing frame: {e}", exc_info=True)
        raise


def classify_frame(
    frame: np.ndarray,
    model: Model,
    class_names: list
) -> Tuple[str, float]:
    """
    對影像幀進行分類
    
    Args:
        frame: 原始影像幀
        model: 已載入的 Keras 模型
        class_names: 類別名稱列表
        
    Returns:
        Tuple[str, float]: (類別名稱, 信心分數)
        
    Raises:
        ValueError: 如果預測失敗
    """
    try:
        # 預處理影像
        processed_frame = preprocess_frame(frame)
        
        # 進行預測
        prediction = model.predict(processed_frame, verbose=0)
        
        # 找出最高信心度的類別
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = float(prediction[0][index])
        
        logger.debug(
            f"Classification result: {class_name} "
            f"(confidence: {confidence_score:.2%})"
        )
        
        return class_name, confidence_score
        
    except Exception as e:
        logger.error(f"Error classifying frame: {e}", exc_info=True)
        raise ValueError(f"Classification failed: {e}")


def is_person_detected(class_name: str, confidence_score: float) -> bool:
    """
    判斷是否檢測到人
    
    Args:
        class_name: 分類名稱
        confidence_score: 信心分數 (0-1)
        
    Returns:
        True 如果檢測到人且信心度足夠
    """
    config = Config()
    return (
        class_name == 'Class 1' and
        confidence_score >= config.analysis.MIN_CONFIDENCE
    )


def is_session_end(class_name: str) -> bool:
    """
    判斷是否應該結束分析會話
    
    Args:
        class_name: 分類名稱
        
    Returns:
        True 如果檢測到 Class 2（會話結束標記）
    """
    return class_name == 'Class 2'
