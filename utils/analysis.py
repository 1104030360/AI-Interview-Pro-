"""
情緒分析工具模組

提供使用 DeepFace 進行情緒、年齡、性別分析的功能。
"""
import time
import numpy as np
from typing import Optional, Dict, Any, List
from deepface import DeepFace

from config import Config
from utils.logging_config import get_logger
from exceptions import AnalysisError

logger = get_logger(__name__)


def analyze_with_demographics(
    frame: np.ndarray,
    class_name: str,
    confidence_score: float
) -> Optional[Dict[str, Any]]:
    """
    分析影像的情緒、年齡和性別
    
    Args:
        frame: 影像幀
        class_name: 分類名稱
        confidence_score: 分類信心分數
        
    Returns:
        包含分析結果的字典，如果分析失敗則返回 None
        
    Example:
        >>> result = analyze_with_demographics(frame, 'Class 1', 0.95)
        >>> print(result['emotion'], result['age'], result['gender'])
    """
    try:
        # 使用 DeepFace 分析
        analyze_result = DeepFace.analyze(
            frame,
            actions=['emotion', 'age', 'gender'],
            enforce_detection=False
        )
        
        # 提取結果
        emotion = analyze_result[0]['dominant_emotion']
        age = round(analyze_result[0]['age'])
        
        gender_prob = analyze_result[0]['gender']
        gender = max(gender_prob, key=gender_prob.get)
        gender_confidence = round(gender_prob[gender], 2)
        
        result = {
            'class_name': class_name,
            'confidence_score': np.round(confidence_score * 100, 2),
            'emotion': emotion,
            'age': age,
            'gender': gender,
            'gender_confidence': gender_confidence
        }
        
        logger.debug(
            f"Demographics analysis: emotion={emotion}, age={age}, "
            f"gender={gender} ({gender_confidence}%)"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in demographics analysis: {e}", exc_info=True)
        return None


def analyze_emotions_only(
    frame: np.ndarray,
    class_name: str,
    confidence_score: float
) -> Optional[Dict[str, Any]]:
    """
    僅分析情緒（不分析年齡和性別）
    
    Args:
        frame: 影像幀
        class_name: 分類名稱
        confidence_score: 分類信心分數
        
    Returns:
        包含情緒分析結果的字典，如果分析失敗則返回 None
    """
    try:
        # 使用 DeepFace 僅分析情緒
        analyze_result = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=False
        )
        
        emotion = analyze_result[0]['dominant_emotion']
        
        result = {
            'class_name': class_name,
            'confidence_score': np.round(confidence_score * 100, 2),
            'emotion': emotion
        }
        
        logger.debug(f"Emotion-only analysis: {emotion}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in emotion analysis: {e}", exc_info=True)
        return None


def analyze_frame_with_retry(
    frame: np.ndarray,
    class_name: str,
    confidence_score: float,
    include_demographics: bool = True,
    max_retries: int = 3,
    retry_delay: float = 0.5
) -> Optional[Dict[str, Any]]:
    """
    帶重試機制的影像分析
    
    Args:
        frame: 影像幀
        class_name: 分類名稱
        confidence_score: 分類信心分數
        include_demographics: 是否包含年齡和性別分析
        max_retries: 最大重試次數
        retry_delay: 重試延遲（秒）
        
    Returns:
        分析結果字典，失敗則返回 None
    """
    analyze_func = (
        analyze_with_demographics if include_demographics 
        else analyze_emotions_only
    )
    
    for attempt in range(max_retries):
        result = analyze_func(frame, class_name, confidence_score)
        
        if result is not None:
            return result
            
        if attempt < max_retries - 1:
            logger.warning(
                f"Analysis attempt {attempt + 1} failed, "
                f"retrying in {retry_delay}s..."
            )
            time.sleep(retry_delay)
    
    logger.error(f"Analysis failed after {max_retries} attempts")
    return None


def categorize_emotion(emotion: str) -> str:
    """
    將情緒分類為正面、負面或中性
    
    Args:
        emotion: 情緒名稱 (happy, sad, angry, etc.)
        
    Returns:
        情緒類別: 'positive', 'negative', 或 'neutral'
    """
    emotion_categories = {
        'positive': ['happy', 'surprise'],
        'negative': ['angry', 'sad'],
        'neutral': ['neutral', 'disgust', 'fear']
    }
    
    for category, emotions in emotion_categories.items():
        if emotion in emotions:
            return category
    
    logger.warning(f"Unknown emotion: {emotion}, categorizing as neutral")
    return 'neutral'


def map_emotion_to_score(emotion: str) -> int:
    """
    將情緒映射為數值分數
    
    Args:
        emotion: 情緒名稱
        
    Returns:
        情緒分數: 1 (正面), 0 (中性), -1 (負面)
    """
    category = categorize_emotion(emotion)
    
    mapping = {
        'positive': 1,
        'neutral': 0,
        'negative': -1
    }
    
    return mapping[category]


def calculate_emotion_statistics(
    emotions: List[str]
) -> Dict[str, float]:
    """
    計算情緒統計資訊
    
    Args:
        emotions: 情緒列表
        
    Returns:
        包含統計資訊的字典
        
    Example:
        >>> stats = calculate_emotion_statistics(['happy', 'sad', 'neutral'])
        >>> print(stats['positive_percentage'])  # 0.33
    """
    if not emotions:
        return {
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_percentage': 0.0,
            'negative_percentage': 0.0,
            'neutral_percentage': 0.0,
            'total_count': 0
        }
    
    positive_count = sum(1 for e in emotions if categorize_emotion(e) == 'positive')
    negative_count = sum(1 for e in emotions if categorize_emotion(e) == 'negative')
    neutral_count = sum(1 for e in emotions if categorize_emotion(e) == 'neutral')
    
    total = len(emotions)
    
    return {
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'positive_percentage': round(positive_count / total, 2),
        'negative_percentage': round(negative_count / total, 2),
        'neutral_percentage': round(neutral_count / total, 2),
        'total_count': total
    }


def calculate_satisfaction_score(
    emotions: List[str],
    baseline_score: int = None
) -> float:
    """
    計算滿意度分數
    
    Args:
        emotions: 情緒列表
        baseline_score: 基準分數（從 Config 讀取如果未提供）
        
    Returns:
        滿意度分數 (0-100)
    """
    if not emotions:
        logger.warning("No emotions provided for score calculation")
        return 0.0
    
    config = Config()
    if baseline_score is None:
        baseline_score = config.analysis.BASELINE_SCORE
    
    stats = calculate_emotion_statistics(emotions)
    
    remain = 100 - baseline_score
    score = (
        baseline_score +
        stats['negative_percentage'] * remain * (-1) +
        stats['neutral_percentage'] * remain * 0 +
        stats['positive_percentage'] * remain * 1
    )
    
    logger.info(
        f"Satisfaction score: {score:.1f} "
        f"(P:{stats['positive_percentage']:.0%}, "
        f"N:{stats['negative_percentage']:.0%}, "
        f"Ne:{stats['neutral_percentage']:.0%})"
    )
    
    return round(score, 1)
