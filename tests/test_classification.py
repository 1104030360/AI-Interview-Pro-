"""
測試 classification 模組
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch

from utils.classification import (
    preprocess_frame,
    classify_frame,
    is_person_detected,
    is_session_end
)


class TestPreprocessFrame:
    """測試 preprocess_frame 函式"""
    
    def test_preprocess_frame_basic(self):
        """測試基本的影像預處理"""
        # 建立測試影像 (100x100 RGB)
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = preprocess_frame(frame, target_size=(224, 224))
        
        # 驗證輸出形狀
        assert result.shape == (1, 224, 224, 3)
        
        # 驗證數值範圍（應該在 -1 到 1 之間）
        assert result.min() >= -1
        assert result.max() <= 1
    
    def test_preprocess_frame_normalization(self):
        """測試正規化是否正確"""
        # 建立白色影像（255, 255, 255）
        white_frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        result = preprocess_frame(white_frame)
        
        # 255 / 127.5 - 1 = 1
        assert np.allclose(result, 1.0, atol=0.01)
    
    def test_preprocess_frame_different_sizes(self):
        """測試不同的目標尺寸"""
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = preprocess_frame(frame, target_size=(128, 128))
        
        assert result.shape == (1, 128, 128, 3)


class TestClassifyFrame:
    """測試 classify_frame 函式"""
    
    def test_classify_frame_with_mock_model(self):
        """使用 mock 模型測試分類"""
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Mock 模型
        mock_model = Mock()
        mock_model.predict.return_value = np.array([[0.2, 0.8]])
        
        class_names = ['Class 1', 'Class 2']
        
        class_name, confidence = classify_frame(frame, mock_model, class_names)
        
        assert class_name == 'Class 2'
        assert confidence == 0.8
        assert mock_model.predict.called
    
    def test_classify_frame_class_1(self):
        """測試 Class 1 分類"""
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        mock_model = Mock()
        mock_model.predict.return_value = np.array([[0.95, 0.05]])
        
        class_names = ['Class 1', 'Class 2']
        
        class_name, confidence = classify_frame(frame, mock_model, class_names)
        
        assert class_name == 'Class 1'
        assert confidence == 0.95


class TestIsPersonDetected:
    """測試 is_person_detected 函式"""
    
    def test_person_detected_high_confidence(self):
        """測試高信心度的人物偵測"""
        assert is_person_detected('Class 1', 0.95) is True
    
    def test_person_detected_low_confidence(self):
        """測試低信心度的人物偵測"""
        assert is_person_detected('Class 1', 0.5) is False
    
    def test_person_not_detected(self):
        """測試非人物類別"""
        assert is_person_detected('Class 2', 0.95) is False
    
    def test_person_detected_exact_threshold(self):
        """測試信心度閾值邊界"""
        # 假設閾值是 0.8
        assert is_person_detected('Class 1', 0.8) is True
        assert is_person_detected('Class 1', 0.79) is False


class TestIsSessionEnd:
    """測試 is_session_end 函式"""
    
    def test_session_end_detected(self):
        """測試會話結束偵測"""
        assert is_session_end('Class 2') is True
    
    def test_session_continues(self):
        """測試會話繼續"""
        assert is_session_end('Class 1') is False
        assert is_session_end('Unknown') is False
