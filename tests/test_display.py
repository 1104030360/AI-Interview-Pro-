"""
測試 display 模組
"""
import pytest
import numpy as np
import cv2
from unittest.mock import patch, Mock

from utils.display import (
    resize_and_flip_frame,
    create_split_screen
)


class TestResizeAndFlipFrame:
    """測試 resize_and_flip_frame 函式"""
    
    def test_resize_only(self):
        """測試僅調整大小"""
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = resize_and_flip_frame(frame, target_size=(200, 150), flip=False)
        
        assert result.shape == (150, 200, 3)
    
    def test_resize_and_flip(self):
        """測試調整大小並翻轉"""
        # 建立一個簡單的測試圖案
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        frame[:, :5, :] = 255  # 左半邊白色
        
        result = resize_and_flip_frame(frame, target_size=(10, 10), flip=True)
        
        # 翻轉後右半邊應該是白色
        assert np.all(result[:, 5:, :] == 255)
        assert np.all(result[:, :5, :] == 0)
    
    def test_default_size(self):
        """測試預設尺寸"""
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = resize_and_flip_frame(frame, target_size=(768, 480))
        
        assert result.shape == (480, 768, 3)


class TestCreateSplitScreen:
    """測試 create_split_screen 函式"""
    
    def test_horizontal_split(self):
        """測試水平分割"""
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        result = create_split_screen(frame1, frame2, orientation='horizontal')
        
        # 水平合併應該是 (100, 200, 3)
        assert result.shape == (100, 200, 3)
        
        # 左邊應該是黑色
        assert np.all(result[:, :100, :] == 0)
        
        # 右邊應該是白色
        assert np.all(result[:, 100:, :] == 255)
    
    def test_vertical_split(self):
        """測試垂直分割"""
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        result = create_split_screen(frame1, frame2, orientation='vertical')
        
        # 垂直合併應該是 (200, 100, 3)
        assert result.shape == (200, 100, 3)
        
        # 上面應該是黑色
        assert np.all(result[:100, :, :] == 0)
        
        # 下面應該是白色
        assert np.all(result[100:, :, :] == 255)
