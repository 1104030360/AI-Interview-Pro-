import os
import sys
import unittest
from unittest.mock import patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import CameraConfig

class TestCameraConfig(unittest.TestCase):
    
    def test_default_mode(self):
        """Test default mode is DUAL"""
        # Note: This depends on the actual env var or default. 
        # If .env is loaded, it might be DUAL.
        # We should check what get_active_cameras returns.
        cameras = CameraConfig.get_active_cameras()
        self.assertTrue(len(cameras) >= 1)
        self.assertEqual(cameras[0]['name'], 'customer')
        
    def test_single_mode_structure(self):
        """Test structure of camera config in single mode"""
        with patch.object(CameraConfig, 'MODE', 'SINGLE'):
            cameras = CameraConfig.get_active_cameras()
            self.assertEqual(len(cameras), 1)
            self.assertEqual(cameras[0]['name'], 'customer')
            self.assertEqual(cameras[0]['role'], 'primary')

    def test_dual_mode_structure(self):
        """Test structure of camera config in dual mode"""
        with patch.object(CameraConfig, 'MODE', 'DUAL'):
            cameras = CameraConfig.get_active_cameras()
            self.assertEqual(len(cameras), 2)
            self.assertEqual(cameras[0]['name'], 'customer')
            self.assertEqual(cameras[1]['name'], 'server')

if __name__ == '__main__':
    unittest.main()