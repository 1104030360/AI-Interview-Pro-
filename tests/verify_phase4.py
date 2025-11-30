import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from project_refactored import EmotionAnalysisSystem
from config import Config

class TestPhase4Verification(unittest.TestCase):
    
    def setUp(self):
        # Mock cv2
        self.cv2_patcher = patch('project_refactored.cv2')
        self.mock_cv2 = self.cv2_patcher.start()
        
        # Mock VideoCapture
        self.mock_cap = MagicMock()
        self.mock_cap.isOpened.return_value = True
        self.mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        self.mock_cap.get.return_value = 640 # Width/Height
        self.mock_cv2.VideoCapture.return_value = self.mock_cap
        
        # Mock DeepFace
        self.deepface_patcher = patch('utils.analysis.DeepFace')
        self.mock_deepface = self.deepface_patcher.start()
        self.mock_deepface.analyze.return_value = [{'dominant_emotion': 'happy', 'age': 25, 'gender': 'Man'}]
        
        # Mock Config
        self.config_patcher = patch('project_refactored.Config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.camera.fps = 30
        self.mock_config.camera.CAMERA_WIDTH = 640
        self.mock_config.camera.CAMERA_HEIGHT = 480
        
        # Mock utils functions that might use cv2 or file system
        patch('project_refactored.open_camera_with_retry', return_value=self.mock_cap).start()
        patch('project_refactored.configure_camera').start()
        patch('project_refactored.create_video_writer').start()
        patch('project_refactored.generate_all_charts').start()
        patch('project_refactored.generate_combined_wave_chart').start()
        
        # Setup output dirs
        self.test_dir = Path('test_output')
        self.test_dir.mkdir(exist_ok=True)
        self.mock_config.paths.WEB_STATIC_DIR = self.test_dir

    def tearDown(self):
        self.cv2_patcher.stop()
        self.deepface_patcher.stop()
        self.config_patcher.stop()
        patch.stopall()
        
        # Cleanup
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_single_mode_execution(self):
        """Test execution in SINGLE mode"""
        print("\nTesting SINGLE mode...")
        
        # Setup Single Mode Config
        self.mock_config.camera.MODE = 'SINGLE'
        self.mock_config.camera.get_active_cameras.return_value = [{
            'id': 0, 'name': 'customer', 'role': 'primary'
        }]
        
        system = EmotionAnalysisSystem()
        
        # Run for a few frames then stop
        # We need to mock process_frame to return 'stop' eventually or just break the loop
        # Here we'll let it run once and then force exit
        with patch.object(system, 'process_frame', side_effect=['happy', 'stop']):
            system.run()
            
        # Verify JSON output
        json_path = self.test_dir / 'data' / 'analysis_result.json'
        self.assertTrue(json_path.exists())
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        self.assertEqual(data['ai_text3'], "（單鏡頭模式：無服務員數據）")
        self.assertIn('total_score', data)
        self.assertEqual(len(data['charts']), 2) # Should only have customer charts

    def test_dual_mode_execution(self):
        """Test execution in DUAL mode"""
        print("\nTesting DUAL mode...")
        
        # Setup Dual Mode Config
        self.mock_config.camera.MODE = 'DUAL'
        self.mock_config.camera.get_active_cameras.return_value = [
            {'id': 0, 'name': 'customer', 'role': 'primary'},
            {'id': 1, 'name': 'server', 'role': 'secondary'}
        ]
        
        system = EmotionAnalysisSystem()
        
        # Run loop
        with patch.object(system, 'process_frame', side_effect=['happy', 'happy', 'stop', 'stop']):
            system.run()
            
        # Verify JSON output
        json_path = self.test_dir / 'data' / 'analysis_result.json'
        self.assertTrue(json_path.exists())
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        self.assertNotEqual(data['ai_text3'], "（單鏡頭模式：無服務員數據）")
        self.assertTrue(len(data['charts']) >= 3) # Should have combined charts

if __name__ == '__main__':
    unittest.main()
