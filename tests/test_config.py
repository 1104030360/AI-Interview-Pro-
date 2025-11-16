"""
測試 config 模組
"""
import pytest
from pathlib import Path
from unittest.mock import patch
import os

from config import PathConfig, CameraConfig, AnalysisConfig, LogConfig, Config
from exceptions import ConfigurationError


class TestPathConfig:
    """測試 PathConfig"""
    
    def test_paths_from_env(self):
        """測試從環境變數載入路徑"""
        with patch.dict(os.environ, {
            'MODEL_DIR': '/test/model',
            'FONT_DIR': '/test/font'
        }):
            config = PathConfig()
            
            assert str(config.model_dir) == '/test/model'
            assert str(config.font_dir) == '/test/font'
    
    def test_model_path(self):
        """測試模型路徑"""
        with patch.dict(os.environ, {
            'MODEL_DIR': '/test/model'
        }):
            config = PathConfig()
            
            assert str(config.model_path) == '/test/model/keras_model.h5'
    
    def test_labels_path(self):
        """測試標籤路徑"""
        with patch.dict(os.environ, {
            'MODEL_DIR': '/test/model'
        }):
            config = PathConfig()
            
            assert str(config.labels_path) == '/test/model/labels.txt'
    
    def test_font_path(self):
        """測試字體路徑"""
        with patch.dict(os.environ, {
            'FONT_DIR': '/test/font'
        }):
            config = PathConfig()
            
            assert 'NotoSansTC' in str(config.font_path)


class TestCameraConfig:
    """測試 CameraConfig"""
    
    def test_default_values(self):
        """測試預設值"""
        config = CameraConfig()
        
        assert config.fps == 5
        assert config.width == 320
        assert config.height == 240
        assert config.display_width == 768
        assert config.display_height == 480
    
    def test_frame_interval(self):
        """測試幀間隔"""
        config = CameraConfig()
        
        # 預設 FPS 5，間隔應該是 1
        assert config.frame_interval == 1


class TestAnalysisConfig:
    """測試 AnalysisConfig"""
    
    def test_default_values(self):
        """測試預設值"""
        config = AnalysisConfig()
        
        assert config.person_detection_delay == 3
        assert config.demographics_analysis_duration == 8
        assert config.session_end_delay == 3
        assert config.baseline_score == 60
        assert config.min_confidence == 0.8
    
    def test_score_weights(self):
        """測試分數權重"""
        config = AnalysisConfig()
        
        assert config.negative_weight == -1
        assert config.neutral_weight == 0
        assert config.positive_weight == 1


class TestLogConfig:
    """測試 LogConfig"""
    
    def test_default_values(self):
        """測試預設值"""
        config = LogConfig()
        
        assert config.log_level == 'INFO'
        assert config.log_file == 'emotion_analysis.log'
        assert config.max_bytes == 10 * 1024 * 1024
        assert config.backup_count == 5


class TestConfig:
    """測試 Config 整合"""
    
    def test_singleton_pattern(self):
        """測試單例模式"""
        config1 = Config()
        config2 = Config()
        
        # 應該是同一個實例
        assert config1 is config2
    
    def test_all_subconfigs_exist(self):
        """測試所有子配置都存在"""
        config = Config()
        
        assert hasattr(config, 'paths')
        assert hasattr(config, 'camera')
        assert hasattr(config, 'analysis')
        assert hasattr(config, 'log')
        
        assert isinstance(config.paths, PathConfig)
        assert isinstance(config.camera, CameraConfig)
        assert isinstance(config.analysis, AnalysisConfig)
        assert isinstance(config.log, LogConfig)
