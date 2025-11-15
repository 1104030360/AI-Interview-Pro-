"""
顯示工具模組

提供在影像上繪製文字和視覺化分析結果的功能。
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict, Any

from config import Config
from utils.logging_config import get_logger

logger = get_logger(__name__)


def put_text_chinese(
    img: np.ndarray,
    text: str,
    x: int,
    y: int,
    font_size: int = 32,
    color: tuple = (0, 0, 0)
) -> np.ndarray:
    """
    在影像上繪製中文文字
    
    Args:
        img: OpenCV 影像 (numpy array)
        text: 要繪製的文字
        x: X 座標
        y: Y 座標
        font_size: 字體大小
        color: 文字顏色 (B, G, R)
        
    Returns:
        繪製文字後的影像
    """
    try:
        config = Config()
        font_path = config.paths.font_path
        
        # 載入字體
        font = ImageFont.truetype(str(font_path), font_size)
        
        # 轉換為 PIL Image
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        
        # 繪製文字（PIL 使用 RGB，OpenCV 使用 BGR，需要轉換）
        rgb_color = (color[2], color[1], color[0])
        draw.text((x, y), text, font=font, fill=rgb_color)
        
        # 轉回 numpy array
        return np.array(img_pil)
        
    except Exception as e:
        logger.error(f"Error drawing Chinese text: {e}", exc_info=True)
        # 如果失敗，使用 OpenCV 的基本文字（不支援中文）
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                   font_size / 32, color, 2)
        return img


def draw_analysis_results(
    img: np.ndarray,
    results: Dict[str, Any],
    show_demographics: bool = True
) -> np.ndarray:
    """
    在影像上繪製分析結果
    
    Args:
        img: 原始影像
        results: 分析結果字典
        show_demographics: 是否顯示年齡和性別
        
    Returns:
        繪製結果後的影像
    """
    try:
        # 提取結果
        class_name = results.get('class_name', 'Unknown')
        confidence = results.get('confidence_score', 0)
        emotion = results.get('emotion', 'Unknown')
        
        # 繪製分類和信心度
        img = put_text_chinese(
            img,
            f"{class_name}, Confidence: {confidence}%",
            10, 30,
            font_size=28
        )
        
        # 繪製情緒
        img = put_text_chinese(
            img,
            f"Emotion: {emotion}",
            10, 70,
            font_size=28
        )
        
        # 如果有年齡和性別資訊且需要顯示
        if show_demographics:
            age = results.get('age')
            gender = results.get('gender')
            gender_confidence = results.get('gender_confidence')
            
            if age is not None:
                img = put_text_chinese(
                    img,
                    f"Age: {age}",
                    10, 110,
                    font_size=28
                )
            
            if gender is not None and gender_confidence is not None:
                img = put_text_chinese(
                    img,
                    f"Gender: {gender} {gender_confidence}%",
                    10, 150,
                    font_size=28
                )
        
        return img
        
    except Exception as e:
        logger.error(f"Error drawing analysis results: {e}", exc_info=True)
        return img


def resize_and_flip_frame(
    frame: np.ndarray,
    target_size: tuple = (768, 480),
    flip: bool = True
) -> np.ndarray:
    """
    調整影像大小並翻轉
    
    Args:
        frame: 原始影像幀
        target_size: 目標尺寸 (width, height)
        flip: 是否水平翻轉
        
    Returns:
        處理後的影像
    """
    try:
        # 調整大小
        resized = cv2.resize(frame, target_size)
        
        # 翻轉（如鏡像效果）
        if flip:
            resized = cv2.flip(resized, 1)
        
        return resized
        
    except Exception as e:
        logger.error(f"Error resizing/flipping frame: {e}", exc_info=True)
        return frame


def create_split_screen(
    frame1: np.ndarray,
    frame2: np.ndarray,
    orientation: str = 'horizontal'
) -> np.ndarray:
    """
    建立分割畫面
    
    Args:
        frame1: 第一個影像
        frame2: 第二個影像
        orientation: 'horizontal' 或 'vertical'
        
    Returns:
        合併後的影像
    """
    try:
        if orientation == 'horizontal':
            combined = np.hstack((frame1, frame2))
        else:
            combined = np.vstack((frame1, frame2))
        
        return combined
        
    except Exception as e:
        logger.error(f"Error creating split screen: {e}", exc_info=True)
        return frame1
