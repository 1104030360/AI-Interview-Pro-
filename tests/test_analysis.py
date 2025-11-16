"""
測試 analysis 模組
"""
import pytest
from unittest.mock import patch, Mock
import numpy as np

from utils.analysis import (
    categorize_emotion,
    map_emotion_to_score,
    calculate_emotion_statistics,
    calculate_satisfaction_score
)


class TestCategorizeEmotion:
    """測試 categorize_emotion 函式"""
    
    def test_positive_emotions(self):
        """測試正面情緒"""
        assert categorize_emotion('happy') == 'positive'
        assert categorize_emotion('surprise') == 'positive'
    
    def test_negative_emotions(self):
        """測試負面情緒"""
        assert categorize_emotion('angry') == 'negative'
        assert categorize_emotion('sad') == 'negative'
    
    def test_neutral_emotions(self):
        """測試中性情緒"""
        assert categorize_emotion('neutral') == 'neutral'
        assert categorize_emotion('disgust') == 'neutral'
        assert categorize_emotion('fear') == 'neutral'
    
    def test_unknown_emotion(self):
        """測試未知情緒（應該返回 neutral）"""
        assert categorize_emotion('unknown') == 'neutral'


class TestMapEmotionToScore:
    """測試 map_emotion_to_score 函式"""
    
    def test_map_positive(self):
        """測試正面情緒映射"""
        assert map_emotion_to_score('happy') == 1
        assert map_emotion_to_score('surprise') == 1
    
    def test_map_negative(self):
        """測試負面情緒映射"""
        assert map_emotion_to_score('angry') == -1
        assert map_emotion_to_score('sad') == -1
    
    def test_map_neutral(self):
        """測試中性情緒映射"""
        assert map_emotion_to_score('neutral') == 0
        assert map_emotion_to_score('fear') == 0


class TestCalculateEmotionStatistics:
    """測試 calculate_emotion_statistics 函式"""
    
    def test_empty_emotions(self):
        """測試空情緒列表"""
        stats = calculate_emotion_statistics([])
        
        assert stats['positive_count'] == 0
        assert stats['negative_count'] == 0
        assert stats['neutral_count'] == 0
        assert stats['total_count'] == 0
    
    def test_all_positive(self):
        """測試全部正面情緒"""
        emotions = ['happy', 'happy', 'surprise']
        stats = calculate_emotion_statistics(emotions)
        
        assert stats['positive_count'] == 3
        assert stats['negative_count'] == 0
        assert stats['neutral_count'] == 0
        assert stats['positive_percentage'] == 1.0
    
    def test_mixed_emotions(self):
        """測試混合情緒"""
        emotions = ['happy', 'sad', 'neutral', 'angry']
        stats = calculate_emotion_statistics(emotions)
        
        assert stats['positive_count'] == 1
        assert stats['negative_count'] == 2
        assert stats['neutral_count'] == 1
        assert stats['positive_percentage'] == 0.25
        assert stats['negative_percentage'] == 0.5
        assert stats['neutral_percentage'] == 0.25
        assert stats['total_count'] == 4
    
    def test_percentages_sum_to_one(self):
        """測試百分比總和為 1"""
        emotions = ['happy', 'sad', 'neutral']
        stats = calculate_emotion_statistics(emotions)
        
        total_percentage = (
            stats['positive_percentage'] +
            stats['negative_percentage'] +
            stats['neutral_percentage']
        )
        
        assert abs(total_percentage - 1.0) < 0.01


class TestCalculateSatisfactionScore:
    """測試 calculate_satisfaction_score 函式"""
    
    def test_empty_emotions(self):
        """測試空情緒列表"""
        score = calculate_satisfaction_score([])
        assert score == 0.0
    
    def test_all_positive(self):
        """測試全部正面情緒（應該是 100 分）"""
        emotions = ['happy', 'happy', 'surprise']
        score = calculate_satisfaction_score(emotions, baseline_score=60)
        
        # 60 + 40 * 1.0 = 100
        assert score == 100.0
    
    def test_all_negative(self):
        """測試全部負面情緒（應該是 20 分）"""
        emotions = ['angry', 'sad', 'angry']
        score = calculate_satisfaction_score(emotions, baseline_score=60)
        
        # 60 + 40 * (-1.0) = 20
        assert score == 20.0
    
    def test_all_neutral(self):
        """測試全部中性情緒（應該是 60 分）"""
        emotions = ['neutral', 'fear', 'disgust']
        score = calculate_satisfaction_score(emotions, baseline_score=60)
        
        # 60 + 40 * 0 = 60
        assert score == 60.0
    
    def test_mixed_emotions(self):
        """測試混合情緒"""
        # 2 正面, 1 負面, 1 中性 = 50% 正面, 25% 負面, 25% 中性
        emotions = ['happy', 'surprise', 'sad', 'neutral']
        score = calculate_satisfaction_score(emotions, baseline_score=60)
        
        # 60 + 40 * (0.5 * 1 + 0.25 * (-1) + 0.25 * 0)
        # = 60 + 40 * (0.5 - 0.25)
        # = 60 + 40 * 0.25
        # = 60 + 10 = 70
        assert score == 70.0
    
    def test_score_range(self):
        """測試分數範圍在 0-100 之間"""
        # 最差情況
        worst = calculate_satisfaction_score(['angry'] * 10, baseline_score=60)
        assert 0 <= worst <= 100
        
        # 最好情況
        best = calculate_satisfaction_score(['happy'] * 10, baseline_score=60)
        assert 0 <= best <= 100
