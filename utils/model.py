"""
模型載入工具模組

提供載入 Keras 模型和標籤的功能。
"""
import time
from pathlib import Path
from typing import Tuple, List
from keras.models import load_model as keras_load_model, Model

from config import Config
from utils.logging_config import get_logger
from exceptions import ModelLoadError

logger = get_logger(__name__)


def load_keras_model(
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Tuple[Model, List[str]]:
    """
    載入 Keras 模型和類別標籤
    
    Args:
        max_retries: 最大重試次數
        retry_delay: 重試延遲（秒）
        
    Returns:
        Tuple[Model, List[str]]: (模型, 類別名稱列表)
        
    Raises:
        ModelLoadError: 如果載入失敗
    """
    config = Config()
    model_path = config.paths.model_path
    labels_path = config.paths.labels_path
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Loading model from {model_path}...")
            
            # 檢查檔案是否存在
            if not Path(model_path).exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            if not Path(labels_path).exists():
                raise FileNotFoundError(f"Labels file not found: {labels_path}")
            
            # 載入模型
            model = keras_load_model(str(model_path), compile=False)
            logger.info("Model loaded successfully")
            
            # 載入標籤
            with open(labels_path, 'r', encoding='utf-8') as f:
                class_names = [line.strip() for line in f.readlines()]
            
            logger.info(f"Loaded {len(class_names)} class labels")
            
            return model, class_names
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise ModelLoadError(f"Model or labels file not found: {e}")
            
        except Exception as e:
            logger.error(
                f"Error loading model (attempt {attempt + 1}/{max_retries}): {e}",
                exc_info=True
            )
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise ModelLoadError(
                    f"Failed to load model after {max_retries} attempts: {e}"
                )


def validate_model(model: Model, expected_input_shape: tuple = (None, 224, 224, 3)) -> bool:
    """
    驗證模型是否有效
    
    Args:
        model: Keras 模型
        expected_input_shape: 預期的輸入形狀
        
    Returns:
        True 如果模型有效
    """
    try:
        # 檢查模型輸入形狀
        input_shape = model.input_shape
        
        if input_shape != expected_input_shape:
            logger.warning(
                f"Model input shape mismatch: expected {expected_input_shape}, "
                f"got {input_shape}"
            )
            return False
        
        logger.info("Model validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Error validating model: {e}", exc_info=True)
        return False
